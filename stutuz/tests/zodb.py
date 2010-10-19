#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function
from __future__ import unicode_literals

from stutuz.tests import TestBase
from stutuz import db


class ZODB(TestBase):

    def test_read(self):
        """Views can read from the database"""

        with db():
            db['_test'] = 'Victory!'

        @self.app.route('/_test/')
        def read_value():
            return db['_test']

        rv = self.client.get('/_test/')
        self.assert_equal(rv.data, 'Victory!')

    def test_write(self):
        """Views can write to the database"""

        @self.app.route('/_test/<value>')
        def write_value(value):
            db['_test'] = value

        self.client.get('/_test/Written!')

        with db():
            self.assert_equal(db['_test'], 'Written!')
