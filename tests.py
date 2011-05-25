from flask import Flask, Module, request, Response, current_app
from attest import Tests, tempdir, assert_hook

from flaskext.attest import request_context
from flaskext.zodb import ZODB, current_db, current_ctx

from datetime import datetime
import uuid
from flaskext.zodb import (Model,
                           new,
                           PersistentList,
                           PersistentMapping,
                           OOBTree)

from os import path
from ZODB.FileStorage import FileStorage
from ZODB.DemoStorage import DemoStorage


TESTING = True


class TestModel(Model):

    sequence = new(list, [0])
    mapping = new(dict)
    btree = new(OOBTree)
    timestamp = new(datetime.utcnow)
    id = new(uuid.uuid4)
    something_else = None

class CustomInitModel(Model):

    sequence = new(list)

    def __init__(self, sequence):
        self.sequence.extend(sequence)


models = Tests()

@models.test
def init_empty():
    instance = TestModel()
    assert type(instance.sequence) is PersistentList
    assert type(instance.mapping) is PersistentMapping
    assert type(instance.btree) is OOBTree
    assert type(instance.timestamp) is datetime
    assert type(instance.id) is uuid.UUID
    assert instance.something_else is None
    assert instance.sequence is not TestModel().sequence
    assert instance.sequence == [0]

@models.test
def model_kwargs():
    instance = TestModel(sequence=(1, 2, 3),
                         mapping={'foo': 'bar'},
                         btree={'bar': 'foo'})
    assert type(instance.sequence) is PersistentList
    assert type(instance.mapping) is PersistentMapping
    assert type(instance.btree) is OOBTree
    assert instance.sequence == [0, 1, 2, 3]
    assert instance.something_else is None

    instance = TestModel(other='foo', something_else=123)
    assert instance.other == 'foo'
    assert instance.something_else == 123

@models.test
def custom_init():
    instance = CustomInitModel([1,2,3])
    assert type(instance.sequence) is PersistentList
    assert instance.sequence == [1, 2, 3]


db = ZODB()
mod = Module(__name__, name='tests')

@mod.route('/write/')
def store():
    db['data'] = request.args['data']
    return 'Success'

@mod.route('/read/')
def retrieve():
    return db['data']


@request_context
def testapp():
    app = Flask(__name__)
    app.register_module(mod)
    app.config.from_object(__name__)
    with tempdir() as name:
        dbfile = path.join(name, 'test.db')
        app.config['ZODB_STORAGE'] = 'file://%s' % dbfile
        db.init_app(app)
        yield app

zodb = Tests(contexts=[testapp])


@zodb.test
def read_write(client):
    response = client.get('/write/', query_string={'data': 'Hello'})
    assert response == Response('Success')
    with db.transaction() as root:
        assert root['data'] == 'Hello'
    response = client.get('/read/')
    assert response == Response('Hello')

@zodb.test
def request_ctx():
    assert not hasattr(current_ctx, 'zodb_connection')
    db['data'] = 'value'
    assert hasattr(current_ctx, 'zodb_connection')

@zodb.test
def root_factory():
    @db.root_factory
    def get_root(root):
        root['approot'] = 'got root?'
        return root['approot']
    assert 'approot' not in db
    assert not hasattr(current_ctx, 'zodb_root')
    assert db.root == 'got root?'
    assert db['approot'] == 'got root?'
    assert hasattr(current_ctx, 'zodb_root')

@zodb.test
def local_proxy():
    assert current_db.app is current_app._get_current_object()
    assert current_app.extensions['zodb'] == current_db
    assert current_app.extensions['zodb'] is current_db._get_current_object()


storage = Tests()

@storage.context
def simpleapp():
    app = Flask(__name__)
    app.config.from_object(__name__)
    with tempdir() as name:
        dbfile = path.join(name, 'test.db')
        with app.test_request_context():
            yield app, dbfile

@storage.test
def from_uri(app, dbfile):
    app.config['ZODB_STORAGE'] = 'file://%s' % dbfile
    db = ZODB(app)
    assert type(db.db.storage) is FileStorage

@storage.test
def from_callable(app, dbfile):
    app.config['ZODB_STORAGE'] = DemoStorage
    assert type(ZODB(app).db.storage) is DemoStorage


all = Tests([models, zodb, storage])

if __name__ == '__main__':
    all.main()
