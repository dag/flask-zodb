#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from uuid import UUID

from flaskext.zodb import Model, List, Mapping, Timestamp, UUID4

from stutuz.tests import TestBase
from stutuz import db


class TestModel(Model):

    sequence = List
    mapping = Mapping
    timestamp = Timestamp
    id = UUID4
    something_else = None


class ZODB(TestBase):

    def test_model_attributes(self):
        """Model instantiates List and Mapping and factories"""

        instance = TestModel()
        self.assert_is_instance(instance.sequence, List)
        self.assert_is_instance(instance.mapping, Mapping)
        self.assert_is_instance(instance.timestamp, datetime)
        self.assert_is_instance(instance.id, UUID)
        self.assert_is(instance.something_else, None)

    def test_model_kwargs(self):
        """Model init sets attributes with kwargs"""

        instance = TestModel(sequence=(1, 2, 3), mapping={'foo': 'bar'})
        self.assert_is_instance(instance.sequence, List)
        self.assert_is_instance(instance.mapping, Mapping)
        self.assert_sequence_equal(instance.sequence, (1, 2, 3))
        self.assert_is(instance.something_else, None)

        instance = TestModel(other='foo', something_else=123)
        self.assert_equal(instance.other, 'foo')
        self.assert_equal(instance.something_else, 123)

    def test_read(self):
        """Views can read from the database"""

        with db() as root:
            root['_test'] = 'Victory!'

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

        with db() as root:
            self.assert_equal(root['_test'], 'Written!')
