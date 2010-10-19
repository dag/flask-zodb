#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function
from __future__ import unicode_literals

from contextlib import contextmanager

from werkzeug import cached_property
from ZODB.DB import DB
from flask import g
import transaction


class ZODB(object):

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    @cached_property
    def db(self):
        return DB(self.app.config['ZODB_STORAGE']())

    def init_app(self, app):
        assert 'ZODB_STORAGE' in app.config, \
               'ZODB_STORAGE must be configured.'
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['zodb'] = self

        @app.before_request
        def open_db():
            g._zodb_connection = self.db.open()
            transaction.begin()

        @app.after_request
        def close_db(response):
            transaction.commit()
            g._zodb_connection.close()
            return response

    def __setitem__(self, key, value):
        g._zodb_connection.root()[key] = value

    def __getitem__(self, key):
        return g._zodb_connection.root()[key]

    def __delitem__(self, key):
        del g._zodb_connection.root()[key]

    @contextmanager
    def __call__(self):
        try:
            g._zodb_connection = self.db.open()
            transaction.begin()
            yield
        finally:
            transaction.commit()
            g._zodb_connection.close()
