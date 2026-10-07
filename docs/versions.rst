===============
Version History
===============

.. automodule:: flupy

1.0.0
-----

* New Capabilities:
    * Everything


1.1.0
-----

* Remove support for calling instance methods on uninitialized flu class passing an interable as the *self* argument
* Remove `flupy.Fluent` from top level `flupy` public API
* Remove `flupy.with_iter` from API


1.1.2
-----

* Change `Fluent` class name to `flu` and remove class alias to improve docs readability
* Add type hints for `flu.sum`


1.2.5
-----

* Fix CLI helper access inside lambdas, comprehensions, and generator expressions.
* Avoid retaining unmatched left-hand keys in inner joins.
* Preserve the original order of unmatched right-hand rows in full joins.
* Fix ``map_item`` key and value type inference for mappings and sequences.
* Improve typing for ``filter`` with ``TypeGuard``, ``window``, ``zip_longest``, and ``denormalize``.
* Add type-checking tests, fix the window benchmark, and update the contributor guide.
