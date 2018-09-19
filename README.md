# flupy

[![CircleCI](https://circleci.com/gh/olirice/flupy.svg?style=svg)](https://circleci.com/gh/olirice/flupy)

* Process big data in python using method chaining built on generators
* Cross-platform CLI

## Overview
flupy implements a fluent interface for chaining multiple method calls as a single python expression. All flupy methods return generators and are evaluated lazily in depth-first order. This allows flupy expressions to transform arbitrary size data in extremely limited memory.

## Setup

### Requirements

* Python 3.5+

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
$ flu
usage: flu [-h] [-f FILE] command
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

#### Standard Library Imports
The following standard library modules are available to the flu command by default.

```json, os, csv, re, math, random, statistics, itertools, collections```

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

