# Type-check fixtures for Fluent/flu method signatures.
#
# This module is never imported or executed by pytest; it is type-checked by
# mypy from src/tests/test_typing.py, which turns each assert_type() call
# below into its own pytest test. Each assert_type() pins the exact type an
# expression resolves to today, including the calls whose element type is
# Any - this file is the single place to check which methods propagate their
# element type and which resolve to Any.
from typing import Any, List, Tuple, Union

from typing_extensions import assert_type

from flupy import flu
from flupy.fluent import Fluent

# flu(...) returns the `flu` subclass; every chained method below is defined
# on `Fluent` and returns "Fluent[...]" rather than Self, so the type narrows
# from `flu[T]` to `Fluent[T]` as soon as one method is chained.
assert_type(flu([1, 2, 3]), flu[int])
assert_type(flu([1, 2, 3]).map(str), Fluent[str])
assert_type(flu([1, 2, 3]).map(str).filter(lambda x: len(x) > 0), Fluent[str])
assert_type(flu(["1", "2"]).map(int).map(lambda x: x * 2.0), Fluent[float])

# collect / to_list / head / tail overloads
assert_type(flu([1, 2, 3]).collect(), List[int])
assert_type(flu([1, 2, 3]).collect(container_type=tuple), Tuple[int, ...])
assert_type(flu([1, 2, 3]).to_list(), List[int])
assert_type(flu([1, 2, 3]).head(), List[int])
assert_type(flu([1, 2, 3]).head(2, container_type=set), set[int])
assert_type(flu([1, 2, 3]).tail(), List[int])

# first / last: no-default vs default overloads
assert_type(flu([1, 2, 3]).first(), int)
assert_type(flu([1, 2, 3]).first("x"), Union[int, str])
assert_type(flu([1, 2, 3]).last(), int)
assert_type(flu([1, 2, 3]).last(default=0.5), Union[int, float])

# sort: key=None preserves T; key=... still yields Fluent[T]
assert_type(flu([3, 1, 2]).sort(), Fluent[int])
assert_type(flu(["bb", "a"]).sort(key=len), Fluent[str])

# group_by: key=None groups on T itself; key=... groups on the key's return type
assert_type(flu([1, 2]).group_by(), Fluent[Tuple[int, Fluent[int]]])
assert_type(flu([1, 2]).group_by(key=str), Fluent[Tuple[str, Fluent[int]]])

# zip: growing tuple arity per overload, up to 3 extra iterables
assert_type(flu([1]).zip(["a"]), Fluent[Tuple[int, str]])
assert_type(flu([1]).zip(["a"], [1.0]), Fluent[Tuple[int, str, float]])
assert_type(flu([1]).zip(["a"], [1.0], [True]), Fluent[Tuple[int, str, float, bool]])

# zip: a 4th+ iterable falls back to a homogeneous-T tuple; the other
# iterables' element types are not part of the result type
assert_type(flu([1]).zip(["a"], [1.0], [True], [None]), Fluent[Tuple[int, ...]])

# enumerate / chunk
assert_type(flu([1, 2]).enumerate(), Fluent[Tuple[int, int]])
assert_type(flu([1, 2, 3]).chunk(2), Fluent[List[int]])

# a long chain: any bad handoff anywhere breaks the final assert_type
result = flu(range(10)).map(lambda x: x * 2).filter(lambda x: x % 3 == 0).map(str).enumerate()
assert_type(result, Fluent[Tuple[int, str]])

# window() and zip_longest() are homogeneous over T, so both propagate T
assert_type(flu([1, 2]).window(2), Fluent[Tuple[int, ...]])
assert_type(flu([1, 2]).zip_longest(["a", "b"]), Fluent[Tuple[int, ...]])

# map_attr resolves to Any: getattr(x, attr) can't be typed against a runtime string
assert_type(flu([(1, 2)]).map_attr("real"), Fluent[Any])

# flatten resolves to Any: its nesting depth is a runtime int, not expressible
# in the type system
assert_type(flu([[1, [2, 3]]]).flatten(), Fluent[Any])

# denormalize resolves to Any: its self-type constrains T to
# SupportsIteration[Any] via a bound TypeVar, so the inner iterable's element
# type is unconstrained and the output tuple element type is Any
assert_type(flu([[1, 2], [3, 4]]).denormalize(), Fluent[Tuple[Any, ...]])

# an Any produced by one link in a chain stays Any for the rest of the chain
after_leak = flu([(1, 2)]).map_attr("real").map(lambda x: x)
assert_type(after_leak, Fluent[Any])
