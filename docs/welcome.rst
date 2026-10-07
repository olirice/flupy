================
Welcome to Flupy
================

flupy is a lightweight library and CLI for implementing python data pipelines with a fluent interface.


Transformations such as ``map``, ``filter``, and ``take`` process items lazily, allowing pipelines to work with large or infinite inputs. Memory use depends on the operations in the pipeline and the size of individual items.

Memory and evaluation
=====================

* ``map``, ``filter``, and ``take`` stream items without accumulating the input. ``chunk(n)`` and ``window(n)`` buffer up to ``n`` items.
* ``sort``, ``shuffle``, and the default ``group_by()`` load the entire input before returning. They require finite input.
* ``group_by(sort=False)`` skips sorting but buffers each consecutive group before yielding it. An infinite run of one key never yields a group.
* Joins buffer the right-hand input (``other``), which must be finite, and stream the left-hand input.
* ``unique`` retains all distinct keys seen so far. ``tee`` buffers items until all copies have consumed them.
* ``denormalize`` buffers each record's iterable components to form their Cartesian product; those components must be finite.
* ``collect()`` and ``to_list()`` materialize their results. Reductions such as ``count()`` and ``sum()`` consume the input without collecting it, but still require it to finish.

API
===
::

    import json
    from flupy import flu

    logs = open('logs.jl', 'r')

    error_count = (
        flu(logs)
        .map(lambda x: json.loads(x))
        .filter(lambda x: x['level'] == 'ERROR')
        .count()
    )

    print(error_count)
    # 14


CLI
===

The flupy library, and python runtime, are also accessible from `flu` command line utility::

    $ cat logs.txt | flu "_.filter(lambda x: x.startswith('ERROR'))"


For more information about the `flu` command see :doc:`command line <./cli>`.


Getting Started
===============

**Requirements**

Python 3.6+

**Installation**
::

    $ pip install flupy


Example
=======

Since 2008, what domains are our customers comming from?::


    from flupy import flu

    customers = [
        {'name': 'Jane', 'signup_year': 2018, 'email': 'jane@ibm.com'},
        {'name': 'Fred', 'signup_year': 2011, 'email': 'fred@google.com'},
        {'name': 'Lisa', 'signup_year': 2014, 'email': 'jane@ibm.com'},
        {'name': 'Jack', 'signup_year': 2007, 'email': 'jane@apple.com'},
    ]

    pipeline = (
        flu(customers)
        .filter(lambda x: x['signup_year'] > 2008)
        .map_item('email')
        .map(lambda x: x.partition('@')[2])
        .group_by() # defaults to identity
        .map(lambda x: (x[0], x[1].count()))
        .collect()
    )

    print(pipeline)
    # [('google.com', 1), ('ibm.com', 2)]
