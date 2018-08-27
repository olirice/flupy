# flupy

[![CircleCI](https://circleci.com/gh/olirice/chainable/tree/master.svg?style=shield&circle-token=85a918f9c0c015e0d9f747f7c09d808ede0ed488)](https://circleci.com/gh/olirice/chainable/tree/master)

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

### Usage
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

### Motivation

