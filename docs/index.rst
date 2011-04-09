Flask-ZODB
==========

.. module:: flaskext.zodb

ZODB extension for Flask: persistence of native Python objects.

Basic setup::

    from ZODB.FileStorage import FileStorage
    from flask import Flask, redirect, render_template_string
    from flaskext.zodb import ZODB

    ZODB_STORAGE = lambda: FileStorage('app.fs')

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
