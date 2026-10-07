# flupy

<p>

<a href="https://flupy.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/flupy/badge/?version=latest" alt="Tests" height="18"></a>
<a href="https://codecov.io/gh/olirice/flupy"><img src="https://codecov.io/gh/olirice/flupy/branch/master/graph/badge.svg" height="18"></a>
<a href="https://github.com/psf/black">
        <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Codestyle Black" height="18">
    </a>
</p>

<p>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python version" height="18"></a>
  <a href="https://badge.fury.io/py/flupy"><img src="https://badge.fury.io/py/flupy.svg" alt="PyPI version" height="18"></a>
    <a href="https://github.com/olirice/flupy/blob/master/LICENSE"><img src="https://img.shields.io/pypi/l/markdown-subtemplate.svg" alt="License" height="18"></a>
    <a href="https://pypi.org/project/flupy/"><img src="https://img.shields.io/pypi/dm/flupy.svg" alt="Download count" height="18"></a>
</p>

---

**Documentation**: <a href="https://flupy.readthedocs.io/en/latest/" target="_blank">https://flupy.readthedocs.io/en/latest/</a>

**Source Code**: <a href="https://github.com/olirice/flupy" target="_blank">https://github.com/olirice/flupy</a>

---

## Overview
Flupy implements a [fluent interface](https://en.wikipedia.org/wiki/Fluent_interface) for operating on python iterables. Transformations such as `map`, `filter`, and `take` process items lazily, allowing pipelines to work with large or infinite inputs. Memory use depends on the operations in the pipeline and the size of individual items.

You can think of flupy as a light weight, 0 dependency, pure python alternative to the excellent [Apache Spark](https://spark.apache.org/) project.

### Memory and evaluation

- `map`, `filter`, and `take` stream items without accumulating the input. `chunk(n)` and `window(n)` buffer up to `n` items.
- `sort`, `shuffle`, and the default `group_by()` load the entire input before returning. They require finite input.
- `group_by(sort=False)` skips sorting but buffers each consecutive group before yielding it. An infinite run of one key never yields a group.
- Joins buffer the right-hand input (`other`), which must be finite, and stream the left-hand input.
- `unique` retains all distinct keys seen so far. `tee` buffers items until all copies have consumed them.
- `denormalize` buffers each record's iterable components to form their Cartesian product; those components must be finite.
- `collect()` and `to_list()` materialize their results. Reductions such as `count()` and `sum()` consume the input without collecting it, but still require it to finish.

## Setup

### Requirements

* Python 3.10+

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
