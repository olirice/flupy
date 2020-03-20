import time
from collections import deque
from functools import reduce, wraps
from itertools import dropwhile, groupby, islice, takewhile, tee, zip_longest
from random import sample
from typing import (
    Any,
    Callable,
    Collection,
    List,
    Container,
    Tuple,
    ContextManager,
    overload,
    Deque,
    Hashable,
    Iterable,
    Iterator,
    Optional,
    Type,
    TypeVar,
    Generic,
    Set,
    Container,
)

__all__ = ["flu", "with_iter"]

T = TypeVar("T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")


class Empty:
    ...


def identity(x):
    return x


def self_to_flu(func: Callable) -> Callable:
    """Decorates class method to first argument to a Fluent"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        wrapped_args = [Fluent(args[0])] + list(args[1:]) if args else []
        return func(*wrapped_args, **kwargs)

    return wrapper


class Fluent(Generic[T]):
    """A fluent interface to lazy generator functions

   	>>> from flupy import flu
        >>> flu(range(100)).map(lambda x: x**2) \
                           .filter(lambda x: x % 3 == 0) \
                           .chunk(3) \
                           .take(2) \
                           .collect()
        [[0, 9, 36], [81, 144, 225]]
    """

    def __init__(self, iterable: Iterable[T]) -> None:
        iterator = iter(iterable)
        self._iterator: Iterator[T] = iterator

    def __getitem__(self, key):
        if isinstance(key, int) and key >= 0:
            try:
                return next(islice(self._iterator, key, key + 1))
            except StopIteration:
                raise IndexError("Fluent index out of range")
        elif isinstance(key, slice):
            return Fluent(islice(self._iterator, key.start, key.stop, key.step))
        else:
            raise KeyError(
                "Key must be non-negative integer or slice, not {}".format(key)
            )

    ### Summary ###
    @self_to_flu
    def collect(self, n: int = None, container_type = list):
        """Collect items from iterable into a container

            >>> flu.collect(range(4))
            [0, 1, 2, 3]

            >>> flu.collect(range(4), container_type=set)
            {0, 1, 2, 3}

            >>> flu.collect(range(4), n=2)
            [0, 1]
        """
        return container_type([v for v in self.take(n)])

    @self_to_flu
    def sum(self):
        """Sum of elements in the iterable

            >>> flu.sum([1,2,3])
            6

        """
        return sum(self)

    @self_to_flu
    def count(self) -> int:
        """Count of elements in the iterable

            >>> flu.count(['a','b','c'])
            3
        """
        return sum(1 for _ in self)

    @self_to_flu
    def min(self) -> T:
        """Smallest element in the interable

               >>> flu.min([1, 3, 0, 2])
               0
        """
        return min(self)

    @self_to_flu
    def max(self) -> T:
        """Largest element in the interable

               >>> flu.max([0, 3, 2, 1])
               3
        """
        return max(self)

    @self_to_flu
    def first(self, default=Empty()) -> T:
        """Return the first item of the iterable. Raise IndexError if empty or default if provided.

               >>> flu.first([0, 1, 2, 3])
               0
               >>> flu.first([], default='some_default')
               'some default'

        when *default* is not provided and the iterable is empty, raise IndexError
        """
        x = default
        for x in self:
            return x
        if isinstance(x, Empty):
            raise IndexError("Empty iterator")
        return default

    @self_to_flu
    def last(self, default=Empty()) -> T:
        """Return the last item of the iterble. Raise IndexError if empty or default if provided.

               >>> flu.last([0, 1, 2, 3])
               3
               >>> flu.last([], default='some_default')
               'some default'
        """
        x = default
        for x in self:
            pass
        if isinstance(x, Empty):
            raise IndexError("Empty iterator")
        return x

    @self_to_flu
    def head(self, n: int = 10, container_type: Type = list):
        """Returns up to the first *n* elements from the iterable.

               >>> flu.head(range(20))
               [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

               >>> flu.head(range(15), n=2)
               [0, 1]

               >>> flu.head([])
               []
        """
        return self.take(n).collect(container_type=container_type)

    @self_to_flu
    def tail(self, n: int = 10, container_type: Type = list):
        """Return up to the last *n* elements from the iterable

               >>> flu.tail(range(20))
               [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

               >>> flu.tail(range(15), n=2)
               [18, 19]
        """
        for val in self.window(n, fill_value=Empty()):
            pass
        return container_type([x for x in val if not isinstance(x, Empty)])

    ### End Summary ###

    ### Non-Constant Memory ###
    @self_to_flu
    def sort(self, key: Optional[Callable[[Any], Any]] = None, reverse=False) -> 'Fluent[T]':
        """Sort iterable by *key* function if provided or identity otherwise

        Note: sorting loads the entire iterable into memory

               >>> flu.sort([3,6,1]).collect()
               [1, 3, 6]

               >>> flu.sort([3,6,1], reverse=True).collect()
               [6, 3, 1]

               >>> flu.sort([3,-6,1], key=abs).collect()
               [1, 3, -6]
        """
        return Fluent(sorted(self, key=key, reverse=reverse))

    @self_to_flu
    def shuffle(self) -> 'Fluent[T]':
        """Randomize the order of elements in the interable

        Note: shuffle loads the entire iterable into memory

               >>> flu.shuffle([3,6,1]).collect()
               [6, 1, 3]
        """
        dat = self.collect()
        return Fluent(sample(dat, len(dat)))

    @self_to_flu
    def group_by(self, key=identity, sort: bool = True):
        """Yield consecutive keys and groups from the iterable

        *key* is a function to compute a key value used in grouping and sorting for each element. *key* defaults to an identity function which returns the unchaged element

        When the iterable is pre-sorted according to *key*, setting *sort* to False will prevent loading the dataset into memory and improve performance

               >>> flu.group_by([2, 4, 2, 4]).collect()
               [2, <Fluent object>), (4, <Fluent object>)]

        Or, if the iterable is pre-sorted

               >>> flu.group_by([2, 2, 5, 5], sort=False).collect()
               [(2, <Fluent object>), (5, <Fluent object>)]

        Using a key function
               >>>  points = [
                        {'x': 1, 'y': 0},
                        {'x': 4, 'y': 3},
                        {'x': 1, 'y': 5}
                    ]
               >>> key_func = lambda u: u['x']
               >>> flu.group_by(points, key=key_func, sort=True).collect()
               [(1, <Fluent object>), (4, <Fluent object>)]
               """
        gen = self.sort(key) if sort else self
        return Fluent(groupby(gen, key)).map(
            lambda x: (x[0], Fluent([y for y in x[1]]))
        )

    @self_to_flu
    def unique(self, key=lambda x: x) -> 'Fluent[T]':
        """Yield elements that are unique by a *key*.

                >>> flu.unique([2, 3, 2, 3]).collect()
                [2, 3]

                >>> flu.unique([2, -3, -2, 3], key=abs).collect()
                [2, -3]
        """

        def _impl():
            seen: Set[Any] = set()
            for x in self:
                x_hash = key(x)
                if x_hash in seen:
                    continue
                else:
                    seen.add(x_hash)
                    yield x

        return Fluent(_impl())

    ### End Non-Constant Memory ###

    ### Side Effect ###
    @self_to_flu
    def rate_limit(self, per_second=100) -> 'Fluent[T]':
        """Restrict consumption of iterable to n item  *per_second*

                >>> import time
                >>> start_time = time.time()
                >>> flu(range(3)).rate_limit(3).collect()
                >>> print('Runtime', time.time() - start_time)
                1.00126 # approximately 1 second for 3 items
        """

        def _impl():
            wait_time = 1.0 / per_second
            for val in self:
                start_time = time.time()
                yield val
                call_duration = time.time() - start_time
                time.sleep(max(wait_time - call_duration, 0.0))

        return Fluent(_impl())

    @self_to_flu
    def side_effect(
        self,
        func: Callable,
        before: Optional[Callable] = None,
        after: Optional[Callable] = None,
    ) -> 'Fluent[T]':
        """Invoke *func* for each item in the iterable before yielding the item.
        *func* takes a single argument and the output is discarded
        *before* and *after* are optional functions that take no parameters and are executed once before iteration begins
        and after iteration ends respectively. Each will be called exactly once.


            >>> flu(range(2)).side_effect(lambda x: print(f'Collected {x}')).collect()
            Collected 0
            Collected 1
            [0, 1]
        """

        def _impl():
            try:
                if before is not None:
                    before()

                for x in self:
                    func(x)
                    yield x

            finally:
                if after is not None:
                    after()

        return Fluent(_impl())

    ### End Side Effect ###

    @self_to_flu
    def map(self, func: Callable, *args, **kwargs) -> 'Fluent[T]':
        """Apply *func* to each element of iterable

            >>> flu(range(5)).map(lambda x: x*x).collect()
            [0, 1, 4, 9, 16]
        """

        def _impl():
            for val in self._iterator:
                yield func(val, *args, **kwargs)

        return Fluent(_impl())

    @self_to_flu
    def map_item(self, item: Hashable) -> 'Fluent[Any]':
        """Extracts *item* from every element of the iterable

            >>> flu([(2, 4), (2, 5)]).map_item(1).collect()
            [4, 5]

            >>> flu([{'mykey': 8}, {'mykey': 5}]).map_item('mykey').collect()
            [8, 5]
        """
        return self.map(lambda x: x[item])

    @self_to_flu
    def map_attr(self, attr: str) -> 'Fluent[Any]':
        """Extracts the attribute *attr* from each element of the iterable

            >>> from collections import namedtuple
            >>> MyTup = namedtuple('MyTup', ['value', 'backup_val'])
            >>> flu([MyTup(1, 5), MyTup(2, 4)]).map_attr('value').collect()
            [1, 2]
        """
        return self.map(lambda x: getattr(x, attr))

    @self_to_flu
    def filter(self, func: Callable[..., bool], *args, **kwargs) -> 'Fluent[T]':
        """Yield elements of iterable where *func* returns truthy

            >>> flu(range(10)).filter(lambda x: x % 2 == 0).collect()
            [0, 2, 4, 6, 8]
        """

        def _impl():
            for val in self._iterator:
                if func(val, *args, **kwargs):
                    yield val

        return Fluent(_impl())

    @self_to_flu
    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Apply a function of two arguments cumulatively to the items of a sequence,
        from left import to right, so as to reduce the sequence to a single value.

            >>> flu(range(5)).reduce(lambda x, y: x+y)
            10
        """
        return reduce(func, self)

    @overload
    def zip(self, __iter1: Iterable[_T1]) -> 'Fluent[Tuple[T, _T1]]': ...

    @overload
    def zip(self, __iter1: Iterable[_T1], __iter2: Iterable[_T2]) -> 'Fluent[Tuple[T, _T1, _T2]]': ...

    @overload
    def zip(self, __iter1: Iterable[_T1], __iter2: Iterable[_T2], __iter3: Iterable[_T3]) -> 'Fluent[Tuple[T, _T1, _T2, _T3]]': ...

    @overload
    def zip(self, __iter1: Iterable[Any], __iter2: Iterable[Any], __iter3: Iterable[Any], __iter4: Iterable[Any], *iterable: Iterable[Any]) -> 'Fluent[Tuple[T, ...]]': ...

    #@self_to_flu
    def zip(self, *iterable: Iterable[Any]):
        """Yields tuples containing the i-th element from the i-th
        argument in the chainable, and the iterable

            >>> flu(range(5)).zip(range(3, 0, -1)).collect()
            [(0, 3), (1, 2), (2, 1)]
        """
        tup_iter = zip(self._iterator, *iterable)
        return Fluent(tup_iter)

    @self_to_flu
    def zip_longest(self, *iterable: Iterable, fill_value=None):
        """Yields tuples containing the i-th element from the i-th
        argument in the chainable, and the iterable
        Iteration continues until the longest iterable is exhaused.
        If iterables are uneven in length, missing values are filled in with fill value

            >>> flu(range(5)).zip_longest(range(3, 0, -1)).collect()
            [(0, 3), (1, 2), (2, 1), (3, None), (4, None)]


            >>> flu(range(5)).zip_longest(range(3, 0, -1), fill_value='a').collect()
            [(0, 3), (1, 2), (2, 1), (3, 'a'), (4, 'a')]
        """
        return Fluent(zip_longest(self, *iterable, fillvalue=fill_value))

    @self_to_flu
    def enumerate(self, start: int = 0) -> 'Fluent[Tuple[int, T]]':
        """Yields tuples from the chainable where the first element
        is a count from initial value *start*.

            >>> flu(range(5)).zip_longest(range(3, 0, -1)).collect()
            [(0, 3), (1, 2), (2, 1), (3, None), (4, None)]
        """
        return Fluent(enumerate(self, start=start))

    @self_to_flu
    def take(self, n: Optional[int] = None) -> 'Fluent[T]':
        """Yield first *n* items of the iterable

            >>> flu(range(10)).take(2).collect()
            [0, 1]
        """
        return Fluent(islice(self._iterator, n))

    @self_to_flu
    def take_while(self, predicate: Callable) -> 'Fluent[T]':
        """Yield elements from the chainable so long as the predicate is true

            >>> flu(range(10)).take_while(lambda x: x < 3).collect()
            [0, 1, 2]
        """
        return Fluent(takewhile(predicate, self._iterator))

    @self_to_flu
    def drop_while(self, predicate: Callable) -> 'Fluent[T]':
        """Drop elements from the chainable as long as the predicate is true;
        afterwards, return every element

            >>> flu(range(10)).drop_while(lambda x: x < 3).collect()
            [4, 5, 6, 7, 8, 9]
        """
        return Fluent(dropwhile(predicate, self._iterator))

    @self_to_flu
    def chunk(self, n: int) -> 'Fluent[List[T]]':
        """Yield lists of elements from iterable in groups of *n*

        if the iterable is not evenly divisiible by *n*, the final list will be shorter

            >>> flu(range(10)).chunk(3).collect()
            [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        """

        def _impl():
            while True:
                out = list(self.take(n))
                if out:
                    yield out
                else:
                    return

        return Fluent(_impl())

    @self_to_flu
    def flatten(self, depth: int = 1, base_type: Type = None, iterate_strings=False) -> 'Fluent[Any]':
        """Recursively flatten nested iterables (e.g., a list of lists of tuples)
        into non-iterable type or an optional user-defined base_type

        Strings are treated as non-iterable for convenience. set iterate_string=True
        to change that behavior.

            >>> flu([[0, 1, 2], [3, 4, 5]]).flatten().collect()
            [0, 1, 2, 3, 4, 5]

            >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten().collect()
            [0, [1, 2], [3, 4], 5]

            >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten(depth=2).collect()
            [0, 1, 2, 3, 4, 5]

            >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten(depth=2).collect()
            [0, 1, 2, 3, 4, 5]

            >>> flu([1, (2, 2), 4, [5, (6, 6, 6)]]).flatten(base_type=tuple).collect()
            [1, (2, 2), 4, 5, (6, 6, 6)]

            >>> flu([[2, 0], 'abc', 3, [4]]).flatten(iterate_strings=True).collect()
            [2, 0, 'a', 'b', 'c', 3, 4]
        """

        def walk(node, level):
            if (
                ((depth is not None) and (level > depth))
                or (isinstance(node, str) and not iterate_strings)
                or ((base_type is not None) and isinstance(node, base_type))
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

        return Fluent(walk(self, level=0))

    @self_to_flu
    def window(self, n: int, step: int = 1, fill_value: Any = None) -> 'Fluent[Tuple[T, ...]]':
        """Yield a sliding window of width *n* over the given iterable.

        Each window will advance in increments of *step*:

        If the length of the iterable does not evenly divide by the *step*
        the final output is padded with *fill_value*

            >>> flu(range(5)).window(3).collect()
            [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

            >>> flu(range(5)).window(n=3, step=2).collect()
            [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

            >>> flu(range(9)).window(n=4, step=3).collect()
            [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, None)]

            >>> flu(range(9)).window(n=4, step=3, fill_value=-1).collect()
            [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, -1)]
        """

        def _impl():
            if n < 0:
                raise ValueError("n must be >= 0")
            if n == 0:
                yield tuple()
                return
            if step < 1:
                raise ValueError("step must be >= 1")

            window: Deque[Any] = deque([], n)
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

        return Fluent(_impl())

    def __iter__(self) -> 'Fluent[T]':
        return self

    def __next__(self) -> T:
        return next(self._iterator)

    @self_to_flu
    def tee(self, n: int = 2) -> 'Fluent[Fluent[T]]':
        """Return n independent iterators from a single iterable

        once tee() has made a split, the original iterable should not be used
        anywhere else; otherwise, the iterable could get advanced without the
        tee objects being informed

            >>> copy1, copy2 = flu(range(5)).tee()
            >>> copy1.sum()
            10
            >>> copy2.collect()
            [0, 1, 2, 3, 4]
        """
        return Fluent(tee(self, n)).map(Fluent)


flu = Fluent


def with_iter(context_manager: ContextManager):
    with context_manager as cm:
        for rec in cm:
            yield rec
