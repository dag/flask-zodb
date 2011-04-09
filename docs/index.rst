ZODB
====


Links
-----

* `Tutorial <http://zodb.org/documentation/tutorial.html>`_
* `Programming guide <http://zodb.org/documentation/guide/index.html>`_
* `Low-level API <http://docs.zope.org/zope3/Code/ZODB/index.html>`_


API Reference
-------------

Core
~~~~

.. autoclass:: flaskext.zodb.ZODB
    :members:


Optional Conveniences for Persistent Objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: flaskext.zodb
    :members: Model, Factory, BTree, List, Mapping, Timestamp, UUID4


Persistent Objects and Balanced Trees
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. class:: persistent.Persistent

.. class:: persistent.list.PersistentList

.. class:: persistent.mapping.PersistentMapping

.. class:: BTrees.OOBTree.OOBTree
