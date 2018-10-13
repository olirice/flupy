# flupy

[![CircleCI](https://circleci.com/gh/olirice/flupy.svg?style=svg)](https://circleci.com/gh/olirice/flupy)
[![Documentation Status](https://readthedocs.org/projects/flupy/badge/?version=latest)](https://flupy.readthedocs.io/en/latest/?badge=latest)
                

* Process big data in python using method chaining built on generators
* Cross-platform CLI

## Overview
flupy implements a fluent interface for chaining multiple method calls as a single python expression. All flupy methods return generators and are evaluated lazily in depth-first order. This allows flupy expressions to transform arbitrary size data in extremely limited memory.

## Setup

### Requirements

* Python 3.6+

### Installation

Install flupy with pip:
```sh
$ pip install flupy
```

### Library
```python
from itertools import count
from flupy import flu

# Processing an infinite sequence in constant memory
pipeline = flu(count()).map(lambda x: x**2) \
                       .filter(lambda x: x % 517 == 0) \
                       .chunk(5) \
                       .take(3)

for item in pipeline:
  print(item)

# Returns:
# [0, 267289, 1069156, 2405601, 4276624]
# [6682225, 9622404, 13097161, 17106496, 21650409]
# [26728900, 32341969, 38489616, 45171841, 52388644]
```

### CLI
flupy has a highly compatible command line interface that brings lazy piplines to your shell. Inputs to the `flu` command are automatically populated into a `Fluent` context named `_`.
````
$ flu -h
usage: flu [-h] [-f FILE] [-i [IMPORT [IMPORT ...]]] command

flupy: a fluent interface for python

positional arguments:
  command               flupy command to execute on input

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  path to input file
  -i [IMPORT [IMPORT ...]], --import [IMPORT [IMPORT ...]]
                        modules to import
                        Syntax: <module>:<object>:<alias>
                        Examples:
                                'import os' = '-i os'
                                'import os as op_sys' = '-i os::op_sys'
                                'from os import environ' = '-i os:environ'
                                'from os import environ as env' = '-i os:environ:env'
````
#### Pipe Input
```
$ cat logs.txt | flu "_.filter(lambda x: 'ERROR:' in x).head()"
```

#### File Input
```
$ flu -f logs.txt "_.filter(lambda x: 'ERROR:' in x).head()"
```

#### No Input
```
$ flu "flu(range(100)).takewhile(lambda x: x < 20)"
```

#### Helper Functions
```walk_files(path='.') = recursively walk files starting at *path*```

```walk_dirs(path='.') = recursively walk directories starting at *path*```


#### Examples:

Path to all .txt files recursively, starting from current directly
```
flu 'walk_files().filter(lambda x: x.endswith(".txt"))'
```

First 100 prime numbers
```
flu 'flu(count(2)).filter(lambda z: flu(range(2, z-1)).filter(lambda x: z % x == 0).head(1) == []) \
        .take(100)' -i itertools:count
```

