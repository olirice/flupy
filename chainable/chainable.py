from collections import deque
from typing import Callable, Collection, Iterable, Type, Hashable, Optional
from itertools import islice, takewhile, dropwhile, groupby, zip_longest

__all__ = [
    'chainable'
]


class Chainable():
    """Enables chaining of generator producing functions"""

    def __init__(self, iterable: Iterable):
        self._iterable = iter(iterable)

    def __getitem__(self, key):
        """asdf"""
        if isinstance(key, int) and key >= 0:
            return Chainable(islice(self._iterable, key, key + 1))
        elif isinstance(key, slice):
            return Chainable(islice(self._iterable, key.start, key.stop, key.step))
        else:
            raise KeyError("Key must be non-negative integer or slice, not {}"
                           .format(key))

    ### Summary ###
    def collect(self, n: int= None, container_type: Collection= list):
        """Returns *n* values from iterable as type *container_type*

        NOTE: Chainable.collect is not chainable. See Chainable.take
        for chainable equivalent
        """
        return container_type(v for v in self.take(n))

    def sum(self):
        """Sum of elements in the iterable"""
        return sum(self)

    def count(self):
        """Count of elements in the iterable"""
        return sum(1 for _ in self)

    def min(self):
        """Smallest element in the interable"""
        return min(self)

    def max(self):
        """Largest element in the interable"""
        return max(self)
    ### End Summary ###

    ### Non-Constant Memory
    def sort(self, key: Optional[Callable] = None, reverse=False):
        """Sort iterable by *key* function if provided or identity otherwise

        WARNING: sorting loads the entire iterable into memory
        """
        return Chainable(sorted(self, key=key, reverse=reverse))
    ### End Non-Constant Memory

    def map(self, func: Callable, *args, **kwargs):
        """Apply *func* to each element of iterable"""
        def __imp():
            for val in self._iterable:
                yield func(val, *args, **kwargs)
        return Chainable(__imp())

    def map_item(self, item):
        """Extracts *item* from every element of the iterable"""
        return self.map(lambda x: x[item])

    def map_attr(self, attr):
        """Extracts the attribute *attr* from each element of the iterable"""
        return self.map(lambda x: getattr(x, attr))

    def filter(self, func: Callable, *args, **kwargs):
        """Yield elements of iterable where *func* returns truthy"""
        def __imp():
            for val in self._iterable:
                if func(val, *args, **kwargs):
                    yield val
        return Chainable(__imp())

    def zip(self, iterable: Iterable):
        """Yields tuples containing the i-th element from the i-th
        argument in the chainable, and the iterable"""
        return Chainable(zip(self, iterable))

    def zip_longest(self, iterable: Iterable, fillvalue=None):
        """Yields tuples containing the i-th element from the i-th
        argument in the chainable, and the iterable
        Iteration continues until the longest iterable is exhaused.
        If iterables are uneven in length, missing values are filled in with fillvalue
        """
        return Chainable(zip_longest(self, iterable, fillvalue=fillvalue))

    def enumerate(self, start: int = 0):
        """Yields tuples from the chainable where the first element
        is a count from initial value *start*."""
        return Chainable(enumerate(self, start=start))

    def take(self, n: int):
        """Yield first *n* items of the iterable"""
        def __imp():
            return islice(self._iterable, n)
        return Chainable(__imp())

    def takewhile(self, predicate: Callable):
        """Yield elements from the chainable so long as the predicate is true"""
        return Chainable(takewhile(predicate, self._iterable))

    def dropwhile(self, predicate: Callable):
        """Drop elements from the chainable as long as the predicate is true;
        afterwards, return every element"""
        return Chainable(dropwhile(predicate, self._iterable))

    def groupby(self, key=lambda x: x):
        """Yield consecutive keys and groups from the iterable. Key defaults to identify function
        Iterable must be sorted on the sme key function"""
        return Chainable(groupby(self._iterable, key)).map(lambda x: (x[0], Chainable(x[1])))

    def chunk(self, n: int):
        """Yield lists of elements from iterable in groups of *n*

        if the iterable is not evenly divisiible by *n*, the final list will be shorter
        """
        def __imp():
            while True:
                out = list(self.take(n))
                if out:
                    yield out
                else:
                    return
        return Chainable(__imp())

    def flatten(self, depth: int = 1, base_type: Type = None, iterate_strings=False):
        """Recursively flatten nested iterables (e.g., a list of lists of tuples)
        into non-iterable type or an optional user-defined base_type

        Strings are treated as non-iterable for convenience. set iterate_string=True
        to change that behavior.
        """
        def walk(node, level):
            if (
                ((depth is not None) and (level > depth)) or
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
                    for val in walk(child, level + 1):
                        yield val

        return Chainable(walk(self, level=0))

    def window(self, n: int, step: int=1, fill_value: object=None):
        """Yield a sliding window of width *n* over the given iterable.

        Each window will advance in increments of *step*:

        If the length of the iterable does not evenly divide by the *step*
        the final output is padded with *fill_value*
        """
        def _imp():
            if n < 0:
                raise ValueError('n must be >= 0')
            if n == 0:
                yield tuple()
                return
            if step < 1:
                raise ValueError('step must be >= 1')

            window = deque([], n)
            append = window.append

            # Initial deque fill
            for _ in range(n):
                append(next(self, fill_value))
            yield tuple(window)

            # Appending new items to the right causes old items to fall off the left
            i = 0
            for item in self:
                append(item)
                i = (i + 1) % step
                if i % step == 0:
                    yield tuple(window)

            # If there are items from the iterable in the window, pad with the given
            # value and emit them.
            if (i % step) and (step - i < n):
                for _ in range(step - i):
                    append(fill_value)
                yield tuple(window)

        return Chainable(_imp())

    def __iter__(self):
        return self

    def __next__(self):
        return next(self._iterable)

def chainable(iterable: Iterable) -> Chainable:
    return Chainable(iterable)

def map_item(iterable: Iterable, item: Hashable) -> Chainable:
    return Chainable(iterable).map_item(item)

def map_attr(iterable: Iterable, attr: str) -> Chainable:
    return Chainable(iterable).map_attr(attr)
