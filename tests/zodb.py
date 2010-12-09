#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from uuid import UUID

from flask import current_app
from flaskext.zodb import (Model, List, Mapping, BTree,
                           Timestamp, UUID4, current_db,
                           PersistentList, PersistentMapping, OOBTree)
from attest import Assert as var

from tests.tools import flask_tests
from stutuz.extensions import db


class TestModel(Model):

    sequence = List
    mapping = Mapping
    btree = BTree
    timestamp = Timestamp
    id = UUID4
    something_else = None


suite = flask_tests()


@suite.test
def model_attributes(client):
    """Model instantiates factories when Model instantiated"""

    instance = var(TestModel())
    assert instance.sequence.__class__.is_(PersistentList)
    assert instance.mapping.__class__.is_(PersistentMapping)
    assert instance.btree.__class__.is_(OOBTree)
    assert instance.timestamp.__class__.is_(datetime)
    assert instance.id.__class__.is_(UUID)
    assert instance.something_else.is_(None)


@suite.test
def model_kwargs():
    """Model init sets attributes with kwargs"""

    instance = var(TestModel(sequence=(1, 2, 3),
                           mapping={'foo': 'bar'},
                           btree={'bar': 'foo'}))
    assert instance.sequence.__class__.is_(PersistentList)
    assert instance.mapping.__class__.is_(PersistentMapping)
    assert instance.btree.__class__.is_(OOBTree)
    assert instance.sequence == [1, 2, 3]
    assert instance.something_else.is_(None)

    instance = var(TestModel(other='foo', something_else=123))
    assert instance.other == 'foo'
    assert instance.something_else == 123


@suite.test
def read(client):
    """Views can read from the database"""

    with db() as root:
        root['_test'] = 'Victory!'

    @current_app.route('/_test/')
    def read_value():
        return db['_test']

    response = client.get('/_test/')
    assert response.data == 'Victory!'


@suite.test
def write(client):
    """Views can write to the database"""

    @current_app.route('/_test/<value>')
    def write_value(value):
        db['_test'] = value

    client.get('/_test/Written!')

    with db() as root:
        assert var(root['_test']) == 'Written!'


@suite.test
def local_proxy():
    """current_db proxies to the ZODB instance"""

    assert var(current_db.app).is_(current_app._get_current_object())
    assert var(current_app.extensions['zodb']) == current_db
    assert var(current_app.extensions['zodb']).is_(
             current_db._get_current_object())
