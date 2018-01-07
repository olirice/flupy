from typing import Iterable, Callable
from itertools import islice

__all__ = [
    'chainable'
]


class Chainable():
    """Enables chaining of generator producing functions"""

    def __init__(self, iterable: Iterable):
        self._iterable = iter(iterable)

    def map(self, func: Callable, *args, **kwargs):
        """Apply *func* to each element of iterable"""
        def __imp():
            for v in self._iterable:
                yield func(v, *args, **kwargs)
        return Chainable(__imp())

    def filter(self, func: Callable, *args, **kwargs):
        """Yield elements of iterable where *func* returns truthy"""
        def __imp():
            for v in self._iterable:
                if func(v, *args, **kwargs):
                    yield v
        return Chainable(__imp())

    def take(self, n: int):
        """Yield first *n* items of the iterable"""
        def __imp():
            return islice(self._iterable, n)
        return Chainable(__imp())

    def chunk(self, n: int):
        """Yield lists of elements from iterable in groups of *n*

        if the iterable is not evenly divisiible by *n*, the final list will be shorter
        """
        def __imp():
            while True:
                out = list(self.take(n))
                if len(out) > 0:
                    yield out
                else:
                    raise StopIteration
        return Chainable(__imp())

    def __iter__(self):
         return self

    def __next__(self):
        return next(self._iterable)

def chainable(iterable: Iterable) -> Chainable:
    return Chainable(iterable)

