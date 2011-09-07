from __future__ import with_statement

import pytest
import transaction

from flask import Flask
from flaskext.zodb import ZODB
from ZODB.MappingStorage import MappingStorage


STORAGES = [
    'memory://',
    (MappingStorage, {}),
    MappingStorage,
]


db = ZODB()


def pytest_generate_tests(metafunc):
    if 'app' in metafunc.funcargnames:
        for storage in STORAGES:
            app = Flask(__name__)
            db.init_app(app)
            app.config['ZODB_STORAGE'] = storage
            metafunc.addcall(dict(app=app))


def test_single_app_shortcut():
    app = Flask(__name__)
    ext = ZODB(app)
    assert app.extensions['zodb'].ext is ext


def test_connection(app):
    assert not db.is_connected
    with app.test_request_context():
        assert not db.is_connected
        db['answer'] = 42
        assert db['answer'] == 42
        assert db.is_connected
    assert not db.is_connected


def test_commit_transaction(app):
    with app.test_request_context():
        db['answer'] = 42

    with app.test_request_context():
        assert db['answer'] == 42


def test_abort_transaction_on_failure(app):
    with pytest.raises(ZeroDivisionError):
        with app.test_request_context():
            db['answer'] = 42
            assert db['answer'] == 42
            1/0

    with app.test_request_context():
        assert 'answer' not in db


def test_abort_transaction_if_doomed(app):
    with app.test_request_context():
        db['answer'] = 42
        transaction.doom()

    with app.test_request_context():
        assert 'answer' not in db
