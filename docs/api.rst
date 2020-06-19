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
.. automethod:: Fluent.flatten
.. automethod:: Fluent.group_by
.. automethod:: Fluent.window

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

.. automethod:: Fluent.enumerate
.. automethod:: Fluent.map
.. automethod:: Fluent.map_attr
.. automethod:: Fluent.map_item
.. automethod:: Fluent.reduce
.. automethod:: Fluent.zip
.. automethod:: Fluent.zip_longest

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
.. automethod:: Fluent.fold_left
.. automethod:: Fluent.first
.. automethod:: Fluent.last
.. automethod:: Fluent.head
.. automethod:: Fluent.tail
.. automethod:: Fluent.collect

----

Non-Constant Memory
===================

.. automethod:: Fluent.group_by
.. automethod:: Fluent.shuffle
.. automethod:: Fluent.sort
.. automethod:: Fluent.tee
.. automethod:: Fluent.unique
