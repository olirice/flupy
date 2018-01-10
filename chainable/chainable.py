from typing import Iterable, Callable, Type
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
            #TODO(OR): DeprecationWarning PEP 479
            # Don't manually raise StopIteration within a generator
            while True:
                out = list(self.take(n))
                if len(out) > 0:
                    yield out
                else:
                    raise StopIteration
        return Chainable(__imp())

    def flatten(self, depth: int=1, base_type: Type=None, iterate_strings=False):
        """Recursively flatten nested iterables (e.g., a list of lists of tuples)
        into non-iterable type or an optional user-defined base_type

        Strings are treated as non-iterable for convenience. set iterate_string=True
        to change that behavior.
        """
        def walk(node, level):
            if (
                ((depth is not None) and (level > depth)) or
                # TODO(OR): Not python2 compatible
                (isinstance(node, str) and not iterate_strings) or
                ((base_type is not None) and isinstance(node, base_type))
            ):
                yield node
                return

            try:
                tree = iter(node)
            except TypeError:
                yield node
                return
            else:
                for child in tree:
                    for x in walk(child, level + 1):
                        yield x

        return Chainable(walk(self, level=0))



    def __iter__(self):
         return self

    def __next__(self):
        return next(self._iterable)

def chainable(iterable: Iterable) -> Chainable:
    return Chainable(iterable)

