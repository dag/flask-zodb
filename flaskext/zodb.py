from UserDict import IterableUserDict
from contextlib import contextmanager, closing

from collections import MutableMapping, MutableSequence

from werkzeug import cached_property, LocalProxy, ImmutableDict
from ZODB.DB import DB
from repoze.zodbconn.uri import db_from_uri
from flask import _request_ctx_stack, current_app
import transaction
from persistent import Persistent
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from BTrees.OOBTree import OOBTree


class ZODB(IterableUserDict):
    """Initialize extension. Acts like a :class:`dict` during requests,
    proxying the root mapping of the configured storage.

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
            if self.connected:
                if exception is None and not transaction.isDoomed():
                    transaction.commit()
                else:
                    transaction.abort()
                self.connection.close()

    @cached_property
    def db(self):
        """The connection pool for your storage. You can safely ignore
        this.

        :Reference:
            `ZODB.DB.DB
            <http://docs.zope.org/zope3/Code/ZODB/DB/DB/>`_

        """
        storage = self.app.config['ZODB_STORAGE']
        if isinstance(storage, basestring):
            return db_from_uri(storage)
        return DB(storage())

    @property
    def connected(self):
        return hasattr(current_ctx, 'zodb_connection')

    @property
    def connection(self):
        """Request-local database connection. You can safely ignore this.

        :Reference:
            `ZODB.Connection.Connection
            <http://docs.zope.org/zope3/Code/ZODB/Connection/Connection/>`_

        """
        if not self.connected:
            current_ctx.zodb_connection = self.db.open()
            transaction.begin()
        return current_ctx.zodb_connection

    def get_root(self, root):
        return root

    def root_factory(self, get_root):
        """Decorator for setting the root factory, a function that receives
        the real root object and returns an object inside it, to be used as
        a virtual root. Can be used to set defaults and for using different
        root objects for different requests - Flask's context-locals can be
        accessed in here.

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
            with transaction.manager:
                yield connection.root()


class Model(Persistent):
    """Convenience model base. Like :class:`~persistent.Persistent`
    but with a default constructor that sets attributes from keyword
    arguments and with a corresponding repr:

    >>> Model(title='Hello!')
    Model(title='Hello!')
    >>> Model(title='Hello!').title
    'Hello!'

    Declare mutable and dynamic attributes in the class definition:

    If the attribute exists and is a mutable mapping or sequence it is
    updated in-place::

        class Post(Model):
            comments = new(list, ['Hi there!'])

    >>> post = Post(comments=['Hello!'])
    >>> post.comments
    ['Hi there!', 'Hello!']
    >>> type(post.comments)
    <class 'persistent.list.PersistentList'>

    """

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            try:
                attribute = getattr(self, name)
            except AttributeError:
                attribute = None
            if isinstance(attribute, (MutableMapping, OOBTree)):
                attribute.update(value)
            elif isinstance(attribute, MutableSequence):
                attribute.extend(value)
            else:
                setattr(self, name, value)

    def __repr__(self):
        attributes = ', '.join('{0}={1!r}'.format(name, value)
            for (name, value) in vars(self).iteritems())
        return '{0}({1})'.format(self.__class__.__name__, attributes)


class new(object):
    """Declare a class attribute to become a new instance of a type for
    each instance of the class. Uses persistent counterparts for `list` and
    `dict`.

    These are the same::

        class Dice(object):
            def __init__(self):
                self.side = random.randint(1, 6)

        class Dice(object):
            side = new(random.randint, 1, 6)

    >>> Dice().side
    3
    >>> Dice().side
    5

    """

    aliases = ImmutableDict({list: PersistentList,
                             dict: PersistentMapping})

    def __init__(self, constructor, *args, **kwargs):
        self.constructor = self.aliases.get(constructor, constructor)
        self.args, self.kwargs = args, kwargs

    def __get__(self, instance, owner):
        if self not in vars(instance):
            value = self.constructor(*self.args, **self.kwargs)
            vars(instance)[self] = value
        return vars(instance)[self]


#: The :class:`ZODB` instance for the current :class:`~flask.Flask`
#: application.
current_db = LocalProxy(lambda: current_app.extensions['zodb'])

current_ctx = LocalProxy(lambda: _request_ctx_stack.top)
