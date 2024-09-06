# pylint: disable=invalid-name
import time
from collections import defaultdict, deque
from collections.abc import Iterable as IterableType
from functools import reduce
from itertools import dropwhile, groupby, islice, product, takewhile, tee, zip_longest
from random import sample
from typing import (
    Any,
    Callable,
    Collection,
    Deque,
    Generator,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    overload,
)

from typing_extensions import Concatenate, ParamSpec, Protocol

__all__ = ["flu"]


T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
S = TypeVar("S")
P = ParamSpec("P")

CallableTakesIterable = Callable[[Iterable[T]], Collection[T]]


class SupportsEquality(Protocol):
    def __eq__(self, __other: object) -> bool:
        pass


class SupportsGetItem(Protocol[T_co]):
    def __getitem__(self, __k: Hashable) -> T_co:
        pass


class SupportsIteration(Protocol[T_co]):
    def __iter__(self) -> Iterator[T]:
        pass


class SupportsLessThan(Protocol):
    def __lt__(self, __other: Any) -> bool:
        pass


SupportsLessThanT = TypeVar("SupportsLessThanT", bound="SupportsLessThan")


class Empty:
    pass


def identity(x: T) -> T:
    return x


class Fluent(Generic[T]):
    """A fluent interface to lazy generator functions

    >>> from flupy import flu
    >>> (
        flu(range(100))
        .map(lambda x: x**2)
        .filter(lambda x: x % 3 == 0)
        .chunk(3)
        .take(2)
        .to_list()
    )
    [[0, 9, 36], [81, 144, 225]]
    """

    def __init__(self, iterable: Iterable[T]) -> None:
        iterator = iter(iterable)
        self._iterator: Iterator[T] = iterator

    @overload
    def __getitem__(self, index: int) -> T:
        pass

    @overload
    def __getitem__(self, index: slice) -> "Fluent[T]":
        pass

    def __getitem__(self, key: Union[int, slice]) -> Union[T, "Fluent[T]"]:
        if isinstance(key, int) and key >= 0:
            try:
                return next(islice(self._iterator, key, key + 1))
            except StopIteration:
                raise IndexError("flu index out of range")
        elif isinstance(key, slice):
            return flu(islice(self._iterator, key.start, key.stop, key.step))
        else:
            raise KeyError("Key must be non-negative integer or slice, not {}".format(key))

    ### Summary ###
    def collect(self, n: Optional[int] = None, container_type: CallableTakesIterable[T] = list) -> Collection[T]:
        """Collect items from iterable into a container

        >>> flu(range(4)).collect()
        [0, 1, 2, 3]

        >>> flu(range(4)).collect(container_type=set)
        {0, 1, 2, 3}

        >>> flu(range(4)).collect(n=2)
        [0, 1]
        """
        return container_type(self.take(n))

    def to_list(self) -> List[T]:
        """Collect items from iterable into a list

        >>> flu(range(4)).to_list()
        [0, 1, 2, 3]
        """
        return list(self)

    def sum(self) -> Union[T, int]:
        """Sum of elements in the iterable

        >>> flu([1,2,3]).sum()
        6

        """
        return sum(self)  # type: ignore

    def count(self) -> int:
        """Count of elements in the iterable

        >>> flu(['a','b','c']).count()
        3
        """
        return sum(1 for _ in self)

    def min(self: "Fluent[SupportsLessThanT]") -> SupportsLessThanT:
        """Smallest element in the interable

        >>> flu([1, 3, 0, 2]).min()
        0
        """
        return min(self)

    def max(self: "Fluent[SupportsLessThanT]") -> SupportsLessThanT:
        """Largest element in the interable

        >>> flu([0, 3, 2, 1]).max()
        3
        """
        return max(self)

    def first(self, default: Any = Empty()) -> T:
        """Return the first item of the iterable. Raise IndexError if empty or default if provided.

        >>> flu([0, 1, 2, 3]).first()
        0
        >>> flu([]).first(default="some_default")
        'some_default'
        """
        x = default
        for x in self:
            return x
        if isinstance(x, Empty):
            raise IndexError("Empty iterator")
        return default

    def last(self, default: Any = Empty()) -> T:
        """Return the last item of the iterble. Raise IndexError if empty or default if provided.

        >>> flu([0, 1, 2, 3]).last()
        3
        >>> flu([]).last(default='some_default')
        'some_default'
        """
        x: Union[Empty, T] = default
        for x in self:
            pass
        if isinstance(x, Empty):
            raise IndexError("Empty iterator")
        return x

    def head(self, n: int = 10, container_type: CallableTakesIterable[T] = list) -> Collection[T]:
        """Returns up to the first *n* elements from the iterable.

        >>> flu(range(20)).head()
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        >>> flu(range(15)).head(n=2)
        [0, 1]

        >>> flu([]).head()
        []
        """
        return self.take(n).collect(container_type=container_type)

    def tail(self, n: int = 10, container_type: CallableTakesIterable[T] = list) -> Collection[T]:
        """Return up to the last *n* elements from the iterable

        >>> flu(range(20)).tail()
        [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        >>> flu(range(15)).tail(n=2)
        [13, 14]
        """
        val: Union[List[Empty], Tuple[Any, ...]] = [Empty()]
        for val in self.window(n, fill_value=Empty()):
            pass
        return container_type([x for x in val if not isinstance(x, Empty)])

    ### End Summary ###

    ### Non-Constant Memory ###
    def sort(
        self: "Fluent[SupportsLessThanT]",
        key: Optional[Callable[[Any], Any]] = None,
        reverse: bool = False,
    ) -> "Fluent[SupportsLessThanT]":
        """Sort iterable by *key* function if provided or identity otherwise

        Note: sorting loads the entire iterable into memory

        >>> flu([3,6,1]).sort().to_list()
        [1, 3, 6]

        >>> flu([3,6,1]).sort(reverse=True).to_list()
        [6, 3, 1]

        >>> flu([3,-6,1]).sort(key=abs).to_list()
        [1, 3, -6]
        """
        return Fluent(sorted(self, key=key, reverse=reverse))

    def join_left(
        self,
        other: Iterable[_T1],
        key: Callable[[T], Hashable] = identity,
        other_key: Callable[[_T1], Hashable] = identity,
    ) -> "Fluent[Tuple[T, Union[_T1, None]]]":
        """Join the iterable with another iterable using equality between *key* applied to self and *other_key* applied to *other* to identify matching entries

        When no matching entry is found in *other*, entries in the iterable are paired with None

        Note: join_left loads *other* into memory

        >>> flu(range(6)).join_left(range(0, 6, 2)).to_list()
        [(0, 0), (1, None), (2, 2), (3, None), (4, 4), (5, None)]
        """

        def _impl() -> Generator[Tuple[T, Union[_T1, None]], None, None]:

            other_lookup = defaultdict(list)

            for entry_other in other:
                other_lookup[other_key(entry_other)].append(entry_other)

            for entry in self:
                matches: Optional[List[_T1]] = other_lookup.get(key(entry))

                if matches:
                    for match in matches:
                        yield (entry, match)
                else:
                    yield (entry, None)

        return Fluent(_impl())

    def join_inner(
        self,
        other: Iterable[_T1],
        key: Callable[[T], Hashable] = identity,
        other_key: Callable[[_T1], Hashable] = identity,
    ) -> "Fluent[Tuple[T, _T1]]":
        """Join the iterable with another iterable using equality between *key* applied to self and *other_key* applied to *other* to identify matching entries

        When no matching entry is found in *other*, entries in the iterable are filtered from the results

        Note: join_inner loads *other* into memory

        >>> flu(range(6)).join_inner(range(0, 6, 2)).to_list()
        [(0, 0), (2, 2), (4, 4)]

        """

        def _impl() -> Generator[Tuple[T, _T1], None, None]:

            other_lookup = defaultdict(list)

            for entry_other in other:
                other_lookup[other_key(entry_other)].append(entry_other)

            for entry in self:
                matches: List[_T1] = other_lookup[key(entry)]

                for match in matches:
                    yield (entry, match)

        return Fluent(_impl())

    def shuffle(self) -> "Fluent[T]":
        """Randomize the order of elements in the interable

        Note: shuffle loads the entire iterable into memory

        >>> flu([3,6,1]).shuffle().to_list()
        [6, 1, 3]
        """
        dat: List[T] = self.to_list()
        return Fluent(sample(dat, len(dat)))

    def group_by(
        self, key: Callable[[T], Union[T, _T1]] = identity, sort: bool = True
    ) -> "Fluent[Tuple[Union[T,_T1], Fluent[T]]]":
        """Yield consecutive keys and groups from the iterable

        *key* is a function to compute a key value used in grouping and sorting for each element. *key* defaults to an identity function which returns the unchaged element

        When the iterable is pre-sorted according to *key*, setting *sort* to False will prevent loading the dataset into memory and improve performance

        >>> flu([2, 4, 2, 4]).group_by().to_list()
        [2, <flu object>), (4, <flu object>)]

        Or, if the iterable is pre-sorted

        >>> flu([2, 2, 5, 5]).group_by(sort=False).to_list()
        [(2, <flu object>), (5, <flu object>)]

        Using a key function

        >>> points = [
            {'x': 1, 'y': 0},
            {'x': 4, 'y': 3},
            {'x': 1, 'y': 5}
        ]
        >>> key_func = lambda u: u['x']
        >>> flu(points).group_by(key=key_func, sort=True).to_list()
        [(1, <flu object>), (4, <flu object>)]
        """

        gen = self.sort(key) if sort else self
        return Fluent(groupby(gen, key)).map(lambda x: (x[0], flu([y for y in x[1]])))

    def unique(self, key: Callable[[T], Hashable] = identity) -> "Fluent[T]":
        """Yield elements that are unique by a *key*.

        >>> flu([2, 3, 2, 3]).unique().to_list()
        [2, 3]

        >>> flu([2, -3, -2, 3]).unique(key=abs).to_list()
        [2, -3]
        """

        def _impl() -> Generator[T, None, None]:
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
    def rate_limit(self, per_second: Union[int, float] = 100) -> "Fluent[T]":
        """Restrict consumption of iterable to n item  *per_second*

        >>> import time
        >>> start_time = time.time()
        >>> _ = flu(range(3)).rate_limit(3).to_list()
        >>> print('Runtime', int(time.time() - start_time))
        1.00126 # approximately 1 second for 3 items
        """

        def _impl() -> Generator[T, None, None]:
            wait_time = 1.0 / per_second
            for val in self:
                start_time = time.time()
                yield val
                call_duration = time.time() - start_time
                time.sleep(max(wait_time - call_duration, 0.0))

        return Fluent(_impl())

    def side_effect(
        self,
        func: Callable[[T], Any],
        before: Optional[Callable[[], Any]] = None,
        after: Optional[Callable[[], Any]] = None,
    ) -> "Fluent[T]":
        """Invoke *func* for each item in the iterable before yielding the item.
        *func* takes a single argument and the output is discarded
        *before* and *after* are optional functions that take no parameters and are executed once before iteration begins
        and after iteration ends respectively. Each will be called exactly once.


        >>> flu(range(2)).side_effect(lambda x: print(f'Collected {x}')).to_list()
        Collected 0
        Collected 1
        [0, 1]
        """

        def _impl() -> Generator[T, None, None]:
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

    def map(self, func: Callable[Concatenate[T, P], _T1], *args: Any, **kwargs: Any) -> "Fluent[_T1]":
        """Apply *func* to each element of iterable

        >>> flu(range(5)).map(lambda x: x*x).to_list()
        [0, 1, 4, 9, 16]
        """

        def _impl() -> Generator[_T1, None, None]:
            for val in self._iterator:
                yield func(val, *args, **kwargs)

        return Fluent(_impl())

    def map_item(self: "Fluent[SupportsGetItem[T]]", item: Hashable) -> "Fluent[T]":
        """Extracts *item* from every element of the iterable

        >>> flu([(2, 4), (2, 5)]).map_item(1).to_list()
        [4, 5]

        >>> flu([{'mykey': 8}, {'mykey': 5}]).map_item('mykey').to_list()
        [8, 5]
        """

        def _impl() -> Generator[T, None, None]:
            for x in self:
                yield x[item]

        return Fluent(_impl())

    def map_attr(self, attr: str) -> "Fluent[Any]":
        """Extracts the attribute *attr* from each element of the iterable

        >>> from collections import namedtuple
        >>> MyTup = namedtuple('MyTup', ['value', 'backup_val'])
        >>> flu([MyTup(1, 5), MyTup(2, 4)]).map_attr('value').to_list()
        [1, 2]
        """
        return self.map(lambda x: getattr(x, attr))

    def filter(self, func: Callable[Concatenate[T, P], bool], *args: Any, **kwargs: Any) -> "Fluent[T]":
        """Yield elements of iterable where *func* returns truthy

        >>> flu(range(10)).filter(lambda x: x % 2 == 0).to_list()
        [0, 2, 4, 6, 8]
        """

        def _impl() -> Generator[T, None, None]:
            for val in self._iterator:
                if func(val, *args, **kwargs):
                    yield val

        return Fluent(_impl())

    def reduce(self, func: Callable[[T, T], T]) -> T:
        """Apply a function of two arguments cumulatively to the items of the iterable,
        from left to right, so as to reduce the sequence to a single value

        >>> flu(range(5)).reduce(lambda x, y: x + y)
        10
        """
        return reduce(func, self)

    def fold_left(self, func: Callable[[S, T], S], initial: S) -> S:
        """Apply a function of two arguments cumulatively to the items of the iterable,
        from left to right, starting with *initial*, so as to fold the sequence to
        a single value

        >>> flu(range(5)).fold_left(lambda x, y: x + str(y), "")
        '01234'
        """
        return reduce(func, self, initial)

    @overload
    def zip(self, __iter1: Iterable[_T1]) -> "Fluent[Tuple[T, _T1]]":
        ...

    @overload
    def zip(self, __iter1: Iterable[_T1], __iter2: Iterable[_T2]) -> "Fluent[Tuple[T, _T1, _T2]]":
        ...

    @overload
    def zip(
        self, __iter1: Iterable[_T1], __iter2: Iterable[_T2], __iter3: Iterable[_T3]
    ) -> "Fluent[Tuple[T, _T1, _T2, _T3]]":
        ...

    @overload
    def zip(
        self,
        __iter1: Iterable[Any],
        __iter2: Iterable[Any],
        __iter3: Iterable[Any],
        __iter4: Iterable[Any],
        *iterable: Iterable[Any]
    ) -> "Fluent[Tuple[T, ...]]":
        ...

    def zip(
        self, *iterable: Iterable[Any]
    ) -> Union[
        "Fluent[Tuple[T, ...]]",
        "Fluent[Tuple[T, _T1]]",
        "Fluent[Tuple[T, _T1, _T2]]",
        "Fluent[Tuple[T, _T1, _T2, _T3]]",
    ]:
        """Yields tuples containing the i-th element from the i-th
        argument in the instance, and the iterable

        >>> flu(range(5)).zip(range(3, 0, -1)).to_list()
        [(0, 3), (1, 2), (2, 1)]
        """
        # @self_to_flu is not compatible with @overload
        # make sure any usage of self supports arbitrary iterables
        tup_iter = zip(iter(self), *iterable)
        return Fluent(tup_iter)

    def zip_longest(self, *iterable: Iterable[_T1], fill_value: Any = None) -> "Fluent[Tuple[T, ...]]":
        """Yields tuples containing the i-th element from the i-th
        argument in the instance, and the iterable
        Iteration continues until the longest iterable is exhaused.
        If iterables are uneven in length, missing values are filled in with fill value

        >>> flu(range(5)).zip_longest(range(3, 0, -1)).to_list()
        [(0, 3), (1, 2), (2, 1), (3, None), (4, None)]


        >>> flu(range(5)).zip_longest(range(3, 0, -1), fill_value='a').to_list()
        [(0, 3), (1, 2), (2, 1), (3, 'a'), (4, 'a')]
        """
        return Fluent(zip_longest(self, *iterable, fillvalue=fill_value))

    def enumerate(self, start: int = 0) -> "Fluent[Tuple[int, T]]":
        """Yields tuples from the instance where the first element
        is a count from initial value *start*.

        >>> flu([3,4,5]).enumerate().to_list()
        [(0, 3), (1, 4), (2, 5)]
        """
        return Fluent(enumerate(self, start=start))

    def take(self, n: Optional[int] = None) -> "Fluent[T]":
        """Yield first *n* items of the iterable

        >>> flu(range(10)).take(2).to_list()
        [0, 1]
        """
        return Fluent(islice(self._iterator, n))

    def take_while(self, predicate: Callable[[T], bool]) -> "Fluent[T]":
        """Yield elements from the chainable so long as the predicate is true

        >>> flu(range(10)).take_while(lambda x: x < 3).to_list()
        [0, 1, 2]
        """
        return Fluent(takewhile(predicate, self._iterator))

    def drop_while(self, predicate: Callable[[T], bool]) -> "Fluent[T]":
        """Drop elements from the chainable as long as the predicate is true;
        afterwards, return every element

        >>> flu(range(10)).drop_while(lambda x: x < 3).to_list()
        [3, 4, 5, 6, 7, 8, 9]
        """
        return Fluent(dropwhile(predicate, self._iterator))

    def chunk(self, n: int) -> "Fluent[List[T]]":
        """Yield lists of elements from iterable in groups of *n*

        if the iterable is not evenly divisiible by *n*, the final list will be shorter

        >>> flu(range(10)).chunk(3).to_list()
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        """

        def _impl() -> Generator[List[T], None, None]:

            while True:
                vals: List[T] = list(self.take(n))
                if vals:
                    yield vals
                else:
                    return

        return Fluent(_impl())

    def flatten(
        self,
        depth: int = 1,
        base_type: Optional[Type[object]] = None,
        iterate_strings: bool = False,
    ) -> "Fluent[Any]":
        """Recursively flatten nested iterables (e.g., a list of lists of tuples)
        into non-iterable type or an optional user-defined base_type

        Strings are treated as non-iterable for convenience. set iterate_string=True
        to change that behavior.

        >>> flu([[0, 1, 2], [3, 4, 5]]).flatten().to_list()
        [0, 1, 2, 3, 4, 5]

        >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten().to_list()
        [0, [1, 2], [3, 4], 5]

        >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten(depth=2).to_list()
        [0, 1, 2, 3, 4, 5]

        >>> flu([[0, [1, 2]], [[3, 4], 5]]).flatten(depth=2).to_list()
        [0, 1, 2, 3, 4, 5]

        >>> flu([1, (2, 2), 4, [5, (6, 6, 6)]]).flatten(base_type=tuple).to_list()
        [1, (2, 2), 4, 5, (6, 6, 6)]

        >>> flu([[2, 0], 'abc', 3, [4]]).flatten(iterate_strings=True).to_list()
        [2, 0, 'a', 'b', 'c', 3, 4]
        """

        # TODO(OR): Reimplement with strong types
        def walk(node: Any, level: int) -> Generator[T, None, None]:
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

    def denormalize(self: "Fluent[SupportsIteration[Any]]", iterate_strings: bool = False) -> "Fluent[Tuple[Any, ...]]":
        """Denormalize iterable components of each record

        >>> flu([("abc", [1, 2, 3])]).denormalize().to_list()
        [('abc', 1), ('abc', 2), ('abc', 3)]

        >>> flu([("abc", [1, 2])]).denormalize(iterate_strings=True).to_list()
        [('a', 1), ('a', 2), ('b', 1), ('b', 2), ('c', 1), ('c', 2)]

        >>> flu([("abc", [])]).denormalize().to_list()
        []
        """

        def _impl() -> Generator[Tuple[Any, ...], None, None]:
            for record in self:
                iter_elements: List[Iterable[Any]] = []
                element: Any
                for element in record:

                    # Check for string and string iteration is allowed
                    if isinstance(element, str) and iterate_strings:
                        iter_elements.append(element)

                    # Check for string and string iteration is not allowed
                    elif isinstance(element, str):
                        iter_elements.append([element])

                    # Check for iterable
                    elif isinstance(element, IterableType):
                        iter_elements.append(element)

                    # Check for non-iterable
                    else:
                        iter_elements.append([element])

                for row in product(*iter_elements):
                    yield row

        return Fluent(_impl())

    def window(self, n: int, step: int = 1, fill_value: Any = None) -> "Fluent[Tuple[Any, ...]]":
        """Yield a sliding window of width *n* over the given iterable.

        Each window will advance in increments of *step*:

        If the length of the iterable does not evenly divide by the *step*
        the final output is padded with *fill_value*

        >>> flu(range(5)).window(3).to_list()
        [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

        >>> flu(range(5)).window(n=3, step=2).to_list()
        [(0, 1, 2), (2, 3, 4)]

        >>> flu(range(9)).window(n=4, step=3).to_list()
        [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, None)]

        >>> flu(range(9)).window(n=4, step=3, fill_value=-1).to_list()
        [(0, 1, 2, 3), (3, 4, 5, 6), (6, 7, 8, -1)]
        """

        def _impl() -> Generator[Tuple[Any, ...], None, None]:
            if n < 0:
                raise ValueError("n must be >= 0")
            elif n == 0:
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

    def __iter__(self) -> "Fluent[T]":
        return self

    def __next__(self) -> T:
        return next(self._iterator)

    def tee(self, n: int = 2) -> "Fluent[Fluent[T]]":
        """Return n independent iterators from a single iterable

        once tee() has made a split, the original iterable should not be used
        anywhere else; otherwise, the iterable could get advanced without the
        tee objects being informed

        >>> copy1, copy2 = flu(range(5)).tee()
        >>> copy1.sum()
        10
        >>> copy2.to_list()
        [0, 1, 2, 3, 4]
        """
        return Fluent((Fluent(x) for x in tee(self, n)))


class flu(Fluent[T]):
    """A fluent interface to lazy generator functions

    >>> from flupy import flu
    >>> (
            flu(range(100))
            .map(lambda x: x**2)
            .filter(lambda x: x % 3 == 0)
            .chunk(3)
            .take(2)
            .to_list()
        )
    [[0, 9, 36], [81, 144, 225]]
    """
