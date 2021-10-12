=============
API Reference
=============

.. automodule:: flupy


Container
=========

.. autoclass:: flu

----


Grouping
========

.. automethod:: flu.chunk
.. automethod:: flu.flatten
.. automethod:: flu.denormalize
.. automethod:: flu.group_by
.. automethod:: flu.window

----

Selecting
=========

.. automethod:: flu.filter
.. automethod:: flu.take
.. automethod:: flu.take_while
.. automethod:: flu.drop_while
.. automethod:: flu.unique

----

Transforming
============

.. automethod:: flu.enumerate
.. automethod:: flu.join_left
.. automethod:: flu.join_inner
.. automethod:: flu.map
.. automethod:: flu.map_attr
.. automethod:: flu.map_item
.. automethod:: flu.zip
.. automethod:: flu.zip_longest

----

Side Effects
============

.. automethod:: flu.rate_limit
.. automethod:: flu.side_effect

----

Summarizing
===========

.. automethod:: flu.count
.. automethod:: flu.sum
.. automethod:: flu.min
.. automethod:: flu.max
.. automethod:: flu.reduce
.. automethod:: flu.fold_left
.. automethod:: flu.first
.. automethod:: flu.last
.. automethod:: flu.head
.. automethod:: flu.tail
.. automethod:: flu.to_list
.. automethod:: flu.collect

----

Non-Constant Memory
===================

.. automethod:: flu.group_by
.. automethod:: flu.join_left
.. automethod:: flu.join_inner
.. automethod:: flu.shuffle
.. automethod:: flu.sort
.. automethod:: flu.tee
.. automethod:: flu.unique
