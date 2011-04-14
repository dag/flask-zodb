Flask-ZODB
==========

.. module:: flaskext.zodb


Setting it Up
-------------

First, let's stub a basic Flask application::

    from flask import Flask
    app = Flask(__name__)

To set it up for using Flask-ZODB, we need to configure a storage and then
create an extension object bound to our application::

    ZODB_STORAGE = 'file://app.fs'
    app.config.from_object(__name__)

    from flaskext.zodb import ZODB
    db = ZODB(app)

The above uses a filestorage called :file:`app.fs`, located relative to the
working directory -- this is rarely what you want in practice but is good
enough for demonstrative purposes and maybe for development.


Transactions
------------

ZODB relies on transactions to write changes to the storage. Flask-ZODB
provides a transactional context manager that lets us work with the object
store easily::

    with db.transaction() as root:
        root['developers'] = {'Flask': 'Armin Ronacher',
                              'Pyramid': 'Chris McDonough'}

The context manager returns the root object of the storage, which functions
like a :class:`dict`. When the context ends, changes to the root object are
written to the storage unless an exception was raised.

Now we should be able to read this data from the storage, even in a new
process:

>>> with db.transaction() as root:
...     print root['developers']['Flask']
...
Armin Ronacher

Requests in Flask are transactional with Flask-ZODB, so we don't normally
need the above in view functions. The extension object also functions like
a `dict`, proxying to the root object during requests::

    @app.route('/developers/<project>/')
    def developers(project):
        return db['developers'][project]


Mutating Persisted Objects
--------------------------

To avoid writing everything on every transaction, ZODB only writes new
objects, and objects marked as mutated in their ``_p_changed`` attribute.
Types such as `dict` are mutable but don't set this attribute, and built in
types don't even let you set it yourself! This means code like this will
have no effect::

    with db.transaction() as root:
        root['developers']['Python'] = 'Guido van Rossum'

The change to the existing *developers* mapping isn't detected by ZODB. A
way around it is to create a new mapping to override the old one::

    root['developers'] = dict(root['developers'], **{'Python': 'Guido van Rossum'})

While this works, it isn't very neat. A better solution is to wrap objects
in "persistence-aware" types that behave just like the types you're used to
working with, but that mark themselves as mutated when needed. We rewrite
the initiation of the *developers* mapping thus::

    from flaskext.zodb import PersistentMapping
    with db.transaction() as root:
        root['developers'] = PersistentMapping({'Flask': 'Armin Ronacher',
                                                'Pyramid': 'Chris McDonough'})

Now we can mutate the existing object in another transaction without
hassle::

    with db.transaction() as root:
        root['developers']['Python'] = 'Guido van Rossum'


.. ::

    ZODB extension for Flask: persistence of native Python objects.

    Basic setup::

        from flask import Flask, redirect, render_template_string
        from flaskext.zodb import ZODB

        ZODB_STORAGE = 'file://app.fs'

        app = Flask(__name__)
        app.config.from_object(__name__)
        db = ZODB(app)

        @app.route('/')
        @app.route('/<message>')
        def index(message=None):
            if message is not None:
                db['message'] = message
                return redirect('/')
            return render_template_string('Latest message: {{ message }}',
                                          message=db['message'])

    During requests the ``db`` object acts like a Python ``dict``. Any changes
    made to it *directly* will persist, changes made to mutable objects
    within will have to be marked as mutated. This is done for you if you
    inherit :class:`Model` for your own classes and use :attr:`List` and
    :attr:`Mapping` as substitutes for Python's ``list`` and ``dict``.

    Outside of requests, the object can be used as a context manager if
    called, yielding the root object to be used inside the context.


    Links
    -----

    * `Tutorial <http://zodb.org/documentation/tutorial.html>`_
    * `Programming guide <http://zodb.org/documentation/guide/index.html>`_
    * `Low-level API <http://docs.zope.org/zope3/Code/ZODB/index.html>`_


API Reference
-------------

Core
~~~~

.. describe:: ZODB_STORAGE

    Mandatory configuration key for your Flask application, needs to be set
    before :meth:`~ZODB.init_app` (which is called for you if you pass an
    app directly to :class:`ZODB` at construction).

    Should be either a callable that returns a storage::

        from ZODB.DemoStorage import DemoStorage
        # use a lambda if you need to set arguments
        app.config['ZODB_STORAGE'] = DemoStorage

    or a URI as a string, as documented `here
    <http://docs.repoze.org/zodbconn/narr.html>`_::

        app.config['ZODB_STORAGE'] = 'file://app.fs'

.. autoclass:: ZODB
    :members: db, connection

    .. automethod:: init_app

    .. automethod:: root_factory

    .. autoattribute:: root

    .. automethod:: transaction()


Optional Conveniences for Persistent Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Model

.. autoclass:: Factory

.. autodata:: BTree

.. autodata:: List

.. autodata:: Mapping

.. autodata:: Timestamp

.. autodata:: UUID


Persistent Objects and Balanced Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. module:: persistent

.. class:: Persistent


.. module:: persistent.list

.. class:: PersistentList


.. module:: persistent.mapping

.. class:: PersistentMapping


.. module:: BTrees.OOBTree

.. class:: OOBTree
