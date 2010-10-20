#-*- coding:utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import with_statement
from __future__ import print_function
from __future__ import unicode_literals

from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from werkzeug import cached_property
from ZODB.DB import DB
from flask import g
import transaction
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


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
        """Transactional context.

        ::

            with db() as root:
                root['this'] = 'is committed at the end of the context.'

        """
        try:
            connection = self.db.open()
            transaction.begin()
            yield connection.root()
        finally:
            transaction.commit()
            connection.close()


class Factory(object):
    """Set a :class:`Model` attribute with a callable on instantiation.

    ::

        class Dice(Model):
            side = Factory(random.randint, 1, 6)

    ::

        >>> Dice()
        Dice(side=3)
        >>> Dice()
        Dice(side=5)

    """

    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.callable(*self.args, **self.kwargs)


#: UTC timestamp factory
Timestamp = Factory(datetime.utcnow)

#: UUID4 factory
UUID4 = Factory(uuid4)

#: Alias for :class:`persistent.list.PersistentList`
List = PersistentList

#: Alias for :class:`persistent.mapping.PersistentMapping`
Mapping = PersistentMapping


class Model(Persistent):
    """Convinience model base.

    You can subclass :class:`persistent.Persistent` directly if you prefer,
    but this base provides some conviniences.

    Set attributes in instantiation::

        >>> Model(title='Hello!')
        Model(title='Hello!')
        >> Model(title='Hello!').title
        'Hello!'

    Declare mutable and dynamic attributes in the class definition::

        class Post(Model):
            id = UUID4
            posted_on = Timestamp
            comments = List

    ::

        >>> Post()
        Post(id=UUID('c3f043a8-8f1f-4381-89b3-fd1f35265925'),
             posted_on=datetime.datetime(2010, 10, 20, 15, 42, 34, 138015),
             comments=[])
        >>> type(Post().comments)
        <class 'persistent.list.PersistentList'>

    """

    def __init__(self, **kwargs):
        mutable = (List, Mapping)
        callable = (Factory,)
        for name, value in vars(self.__class__).items():
            if value in mutable or isinstance(value, callable):
                setattr(self, name, value())

        for name, value in kwargs.iteritems():
            try:
                attribute = getattr(self, name)
            except AttributeError:
                attribute = None
            if isinstance(attribute, List):
                attribute.extend(value)
            elif isinstance(attribute, Mapping):
                attribute.update(value)
            else:
                setattr(self, name, value)

    def __repr__(self):
        attributes = ', '.join('{0}={1!r}'.format(name, value)
            for (name, value) in vars(self).iteritems())
        return '{0}({1})'.format(self.__class__.__name__, attributes)
