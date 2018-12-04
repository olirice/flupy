=============
API Reference
=============

.. automodule:: flupy


Container
=========

.. autoclass:: Fluent
.. autoclass:: flu

----


Grouping
========

.. automethod:: Fluent.chunk
.. automethod:: Fluent.group_by
.. automethod:: Fluent.window
.. automethod:: Fluent.flatten

----

Selecting
=========

.. automethod:: Fluent.filter
.. automethod:: Fluent.take
.. automethod:: Fluent.take_while
.. automethod:: Fluent.drop_while
.. automethod:: Fluent.unique

----

Transforming
============

.. automethod:: Fluent.map
.. automethod:: Fluent.map_item
.. automethod:: Fluent.map_attr

----

Side Effects
============

.. automethod:: Fluent.rate_limit
.. automethod:: Fluent.side_effect

----

Summarizing
===========

.. automethod:: Fluent.count
.. automethod:: Fluent.sum
.. automethod:: Fluent.min
.. automethod:: Fluent.max
.. automethod:: Fluent.reduce
.. automethod:: Fluent.first
.. automethod:: Fluent.last
.. automethod:: Fluent.head
.. automethod:: Fluent.tail
.. automethod:: Fluent.collect

----

Non-Constant Memory
===================

.. automethod:: Fluent.sort
.. automethod:: Fluent.group_by
.. automethod:: Fluent.unique
