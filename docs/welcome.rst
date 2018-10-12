=======
Welcome
=======

flupy is a lightweight library and CLI for implementing python data pipelines with a fluent_ interface.::


    import json
    from flupy import flu

    logs = open('logs.jl', 'r')

    error_count = flu(logs).map(lambda x: json.loads(x)) \
                           .filter(lambda x: x['level'] == 'ERROR')
                           .count()
    
    print(error_count)
    # 14


Under the hood, flupy is built on generators. That means its pipelines evaluate lazily and use a constant amount of memory no matter how much data are being processed. This allows flupy to tackle Petabyte scale data manipulation as effortlessly as it operates on an empty list.

Goals
=====

- A minimal and intuitive API + CLI
- Lazy, memory efficient evaluation
- Platform agnositc, dependency-free implementation


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





Influencing Projects
====================

- more-itertools_
- pyspark_
- pydash_
- sqlalchemy_
- scala_

.. _fluent: https://en.wikipedia.org/wiki/Fluent_interface
.. _more-itertools: https://github.com/erikrose/more-itertools
.. _pyspark: http://spark.apache.org/docs/2.2.0/api/python/pyspark.html
.. _sqlalchemy: https://www.sqlalchemy.org/
.. _pydash: https://pydash.readthedocs.io/en/latest/index.html
.. _scala: https://www.scala-lang.org/
