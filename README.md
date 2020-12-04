# flupy

<p>

<a href="https://github.com/olirice/flupy/actions"><img src="https://github.com/olirice/flupy/workflows/Tests/badge.svg" alt="Tests" height="18"></a>
<a href="https://flupy.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/flupy/badge/?version=latest" alt="Tests" height="18"></a>
<a href="https://codecov.io/gh/olirice/flupy"><img src="https://codecov.io/gh/olirice/flupy/branch/master/graph/badge.svg" height="18"></a>
<a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Codestyle Black" height="18">
    </a>
<a href="https://github.com/olirice/flupy/actions"><img src="https://github.com/olirice/flupy/workflows/mypyc/badge.svg" alt="mypyc" height="18"></a>
</p>

<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.6+-blue.svg" alt="Python version" height="18"></a>
  <a href="https://badge.fury.io/py/flupy"><img src="https://badge.fury.io/py/flupy.svg" alt="PyPI version" height="18"></a>
    <a href="https://github.com/olirice/flupy/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/markdown-subtemplate.svg" alt="License" height="18"></a>
    <a href="https://pypi.org/project/flupy/"><img src="https://img.shields.io/pypi/dm/flupy.svg" alt="Download count" height="18"></a>
</p>

---

**Documentation**: <a href="https://flupy.readthedocs.io/en/latest/" target="_blank">https://flupy.readthedocs.io/en/latest/</a>

**Source Code**: <a href="https://github.com/olirice/flupy" target="_blank">https://github.com/olirice/flupy</a>

---

## Overview
Flupy implements a [fluent interface](https://en.wikipedia.org/wiki/Fluent_interface) for operating on python iterables. All flupy methods return generators and are evaluated lazily. This allows expressions to transform arbitrary size data in extremely limited memory.

You can think of flupy as a light weight, 0 dependency, pure python alternative to the excellent [Apache Spark](https://spark.apache.org/) project.

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
pipeline = (
    flu(count())
    .map(lambda x: x**2)
    .filter(lambda x: x % 517 == 0)
    .chunk(5)
    .take(3)
)

for item in pipeline:
  print(item)

# Returns:
# [0, 267289, 1069156, 2405601, 4276624]
# [6682225, 9622404, 13097161, 17106496, 21650409]
# [26728900, 32341969, 38489616, 45171841, 52388644]
```

### CLI
The flupy command line interface brings the same syntax for lazy piplines to your shell. Inputs to the `flu` command are auto-populated into a `Fluent` context named `_`.
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
