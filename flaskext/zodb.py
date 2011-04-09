from UserDict import IterableUserDict
from contextlib import contextmanager, closing
from datetime import datetime
from uuid import uuid4

from werkzeug import cached_property, LocalProxy
from ZODB.DB import DB
from flask import _request_ctx_stack, current_app
import transaction
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree


class ZODB(IterableUserDict):
    """Initialize extension.

    ::

        app = Flask(__name__)
        db = ZODB(app)

    Optionally you can create the extension object first and set up the
    application later with :meth:`init_app`.

    """

    app = None

    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Bind this extension object to a Flask application and configure
        it. Useful for `application factories
        <http://flask.pocoo.org/docs/patterns/appfactories/>`_.

        ::

            db = ZODB()

            def create_app():
                app = Flask(__name__)
                db.init_app(app)
                return app

        """
        assert 'ZODB_STORAGE' in app.config, \
               'ZODB_STORAGE must be configured.'
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['zodb'] = self

        @app.teardown_request
        def close_db(exception):
            if exception is None:
                transaction.commit()
            else:
                transaction.abort()
            self.connection.close()

    @cached_property
    def db(self):
        """The connection pool for your :data:`ZODB_STORAGE`. You don't
        usually need to use this directly yourself. See also the
        `reference documentation for this object
        <http://docs.zope.org/zope3/Code/ZODB/DB/DB/index.html>`_."""
        return DB(self.app.config['ZODB_STORAGE']())

    @property
    def connection(self):
        """Request-local database connection."""
        if not hasattr(current_ctx, 'zodb_connection'):
            current_ctx.zodb_connection = self.db.open()
            transaction.begin()
        return current_ctx.zodb_connection

    def get_root(self, root):
        return root

    def root_factory(self, get_root):
        """Decorator for setting the root factory, a function that receives
        the root object and returns an object inside it, to be used as an
        artificial root. Can be used to set defaults and for using
        different root objects for different requests - Flask's
        context-locals can be accessed in here.

        ::

            class Root(Model):
                pass

            @db.root_factory
            def get_root(root):
                return root.setdefault('myapp', Root())

            with app.test_request_context():
                assert db.root is db['myapp']

        The default root factory simply returns the root as-is.

        """
        self.get_root = get_root
        return get_root

    @property
    def root(self):
        """Root object for the request, as defined by the
        :meth:`root_factory`."""
        if not hasattr(current_ctx, 'zodb_root'):
            current_ctx.zodb_root = self.get_root(self.connection.root())
        return current_ctx.zodb_root

    @property
    def data(self):
        return self.connection.root()

    @contextmanager
    def transaction(self):
        """Context manager for a transaction bound connection. Returns the
        root object of the storage. Can be used for transactions outside of
        requests.

        ::

            with db.transaction() as root:
                root['key'] = value

        """
        with closing(self.db.open()) as connection:
            with transaction:
                yield connection.root()


class Factory(object):
    """Set a :class:`Model` attribute with a callable on instantiation.
    Useful for delaying initiation of mutable or dynamic objects.

    ::

        class Dice(Model):
            side = Factory(random.randint, 1, 6)

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

#: Factory for :class:`~persistent.list.PersistentList`
List = Factory(PersistentList)

#: Factory for :class:`~persistent.mapping.PersistentMapping`
Mapping = Factory(PersistentMapping)

#: Factory for an object-to-object balanced tree mapping,
#: an :class:`~BTrees.OOBTree.OOBTree`.
BTree = Factory(OOBTree)


class Model(Persistent):
    """Convinience model base.

    You can subclass :class:`persistent.Persistent` directly if you prefer,
    but this base provides some conviniences.

    Set attributes in instantiation:

    >>> Model(title='Hello!')
    Model(title='Hello!')
    >>> Model(title='Hello!').title
    'Hello!'

    Declare mutable and dynamic attributes in the class definition::

        class Post(Model):
            id = UUID4
            posted_on = Timestamp
            comments = List

    >>> Post()
    Post(id=UUID('c3f043a8-8f1f-4381-89b3-fd1f35265925'),
         posted_on=datetime.datetime(2010, 10, 20, 15, 42, 34, 138015),
         comments=[])
    >>> type(Post().comments)
    <class 'persistent.list.PersistentList'>

    """

    def __init__(self, **kwargs):
        for name in dir(self):
            value = getattr(self, name)
            if isinstance(value, Factory):
                setattr(self, name, value())

        for name, value in kwargs.iteritems():
            try:
                attribute = getattr(self, name)
            except AttributeError:
                attribute = None
            if isinstance(attribute, PersistentList):
                attribute.extend(value)
            elif isinstance(attribute, (PersistentMapping, OOBTree)):
                attribute.update(value)
            else:
                setattr(self, name, value)

    def __repr__(self):
        attributes = ', '.join('{0}={1!r}'.format(name, value)
            for (name, value) in vars(self).iteritems())
        return '{0}({1})'.format(self.__class__.__name__, attributes)


#: The :class:`ZODB` instance for the current :class:`~flask.Flask`
#: application.
current_db = LocalProxy(lambda: current_app.extensions['zodb'])


current_ctx = LocalProxy(lambda: _request_ctx_stack.top)
