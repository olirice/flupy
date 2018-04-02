# Chainable

[![CircleCI](https://circleci.com/gh/olirice/chainable/tree/master.svg?style=shield&circle-token=85a918f9c0c015e0d9f747f7c09d808ede0ed488)](https://circleci.com/gh/olirice/chainable/tree/master)

Process big data in python using method chaining built on generators.

## Overview
chainable implements a 'Chainable' class that enables stringing multiple methods together on a single line. All chainable methods return generators and are evaluated lazily in 'depth-first' order.

## Setup

### Requirements

* Python 3.5+

### Installation

Install chainable with pip:
```sh
$ pip install chainable
```

### Usage
```python
from itertools import count
from chainable import chainable

# Processing an infinite sequence in constant memory
pipeline = chainable(count()) \
                .map(lambda x: x**2) \
                .filter(lambda x: x % 517 == 0) \
                .chunk(5) \
                .take(3)
          
print(next(pipeline)) # prints [0, 267289, 1069156, 2405601, 4276624] 
print(next(pipeline)) # prints [6682225, 9622404, 13097161, 17106496, 21650409] 
print(next(pipeline)) # prints [26728900, 32341969, 38489616, 45171841, 52388644] 
print(next(pipeline)) # raises StopIteration
```

### y tho
When working with large data sets, storing intermediate results of ETL pipelines consume unnecessary memory. A depth-first generator pipline minimize the memory required to process records so the entire dataset doesn't need to fit in-memory.
