================
Welcome to Flupy
================

flupy is a lightweight library and CLI for implementing python data pipelines with a fluent_ interface.::


Under the hood, flupy is built on generators. That means its pipelines evaluate lazily and use a constant amount of memory no matter how much data are being processed. This allows flupy to tackle Petabyte scale data manipulation as easily as it operates on a small list.

API
===
::

    import json
    from flupy import flu

    logs = open('logs.jl', 'r')

    error_count = flu(logs).map(lambda x: json.loads(x)) \
                           .filter(lambda x: x['level'] == 'ERROR')
                           .count()
    
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

A real-world example: Which companies did our customers, who signed up after 2008, come from?::


    from flupy import flu

    customers = [
        {'name': 'Jane', 'signup_year': 2018, 'email': 'jane@ibm.com'},
        {'name': 'Fred', 'signup_year': 2011, 'email': 'fred@google.com'},
        {'name': 'Lisa', 'signup_year': 2014, 'email': 'jane@ibm.com'},
        {'name': 'Jack', 'signup_year': 2007, 'email': 'jane@apple.com'},
    ]

    pipeline = flu(customers).filter(lambda x: x['signup_year'] > 2008) \
                             .map_item('email') \
                             .map(lambda x: x.partition('@')[2]) \
                             .group_by() \
                             .map(lambda x: (x[0], x[1].count())) \
                             .collect()
    
    print(pipeline)
    # [('google.com', 1), ('ibm.com', 2)]
