Flask-ZODB
==========

.. module:: flaskext.zodb


Setting it Up
-------------

First, let's stub a basic Flask application::

  from flask import Flask
  app = Flask(__name__)

To set it up for using Flask-ZODB, we need to configure a storage and then
create an extension object for ZODB which will also initiate the Flask
application for handling ZODB connections::

  app.config['ZODB_STORAGE'] = 'file://app.fs'

  from flaskext.zodb import ZODB
  db = ZODB(app)

The above uses a filestorage called :file:`app.fs`, located relative to the
working directory -- this is rarely what you want in practice but is good
enough for demonstrative purposes and maybe for development.


API Reference
-------------

.. describe:: ZODB_STORAGE

  Flask configuration option which must be set to one of:

  * A URI string supported by zodburi_
  * A tuple ``(storage_factory, db_keyword_args)``
  * A callable ``storage_factory``

  .. _zodburi: https://docs.pylonsproject.org/projects/zodburi/dev/

.. autoclass:: ZODB
  :members:

.. autoclass:: ZODBConnector
  :members:


Persistent Objects
""""""""""""""""""

This module exports some shorthand aliases for the persistent types and
balanced trees commonly used with ZODB.

.. class:: Object

  Alias of :class:`persistent.Persistent`.  Use this as the base class for
  your plain objects instead of :func:`object`, if you intend to save
  the object in ZODB.  This way changes to existing objects are detected
  and saved automatically.

.. class:: List

  Alias of :class:`persistent.list.PersistentList`.  Use this instead of
  :func:`list` for lists that you save in ZODB and changes to it will be
  detected and saved automatically.  Not necessary if you won't be changing
  the list after it is saved.

.. class:: Dict

  Alias of :class:`persistent.mapping.PersistentMapping`.  Use this
  instead of :func:`dict` for mappings that you save in ZODB and that you
  might want to make changes to later.  This way those changes will
  automatically be detected and saved.

.. class:: BTree

  Alias of :class:`BTrees.OOBTree.OOBTree`.  Behaves mostly like
  :class:`Dict` but requires that the keys are orderable and performs
  better on large mappings.  Whereas a :class:`Dict` is fully loaded in
  memory every time it is read, a BTree mapping only loads the items that
  you try to read.
