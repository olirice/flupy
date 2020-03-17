import sys
from itertools import count, cycle

import pytest

from flupy import flu


def test_collect():
    assert flu(range(3)).collect() == [0, 1, 2]
    assert flu(range(3)).collect(container_type=tuple) == (0, 1, 2)
    assert flu(range(3)).collect(n=2) == [0, 1]


def test___getitem__():
    assert flu(range(3))[1] == 1
    assert flu(range(3))[1:].collect() == [1, 2]
    assert flu(range(35))[1:2].collect() == [1]
    assert flu(range(35))[1:3].collect() == [1, 2]


def test_sum():
    gen = flu(range(3))
    assert gen.sum() == 3


def test_reduce():
    gen = flu(range(5))
    assert gen.reduce(lambda x, y: x + y) == 10


def test_count():
    gen = flu(range(3))
    assert gen.count() == 3


def test_min():
    gen = flu(range(3))
    assert gen.min() == 0


def test_first():
    gen = flu(range(3))
    assert gen.first() == 0
    gen = flu([])
    with pytest.raises(IndexError):
        gen.first()
    gen = flu([])
    assert gen.first(default=1) == 1


def test_last():
    gen = flu(range(3))
    assert gen.last() == 2
    gen = flu([])
    with pytest.raises(IndexError):
        gen.last()
    gen = flu([])
    assert gen.last(default=1) == 1


def test_head():
    gen = flu(range(30))
    assert gen.head(n=2) == [0, 1]
    gen = flu(range(30))
    assert gen.head(n=3, container_type=set) == set([0, 1, 2])
    gen = flu(range(3))
    assert gen.head(n=50) == [0, 1, 2]


def test_tail():
    gen = flu(range(30))
    assert gen.tail(n=2) == [28, 29]
    gen = flu(range(30))
    assert gen.tail(n=3, container_type=set) == set([27, 28, 29])
    gen = flu(range(3))
    assert gen.tail(n=50) == [0, 1, 2]


def test_max():
    gen = flu(range(3))
    assert gen.max() == 2


def test_unique():
    class NoHash:
        def __init__(self, letter, keyf):
            self.letter = letter
            self.keyf = keyf

    a = NoHash("a", 1)
    b = NoHash("b", 1)
    c = NoHash("c", 2)

    gen = flu([a, b, c]).unique()
    assert gen.collect() == [a, b, c]
    gen = flu([a, b, c]).unique(lambda x: x.letter)
    assert gen.collect() == [a, b, c]
    gen = flu([a, b, c]).unique(lambda x: x.keyf)
    assert gen.collect() == [a, c]


def test_side_effect():
    class FakeFile:
        def __init__(self):
            self.is_open = False
            self.content = []

        def write(self, text):
            if self.is_open:
                self.content.append(text)
            else:
                raise IOError("fake file is not open for writing")

        def open(self):
            self.is_open = True

        def close(self):
            self.is_open = False

    # Test the fake file
    ffile = FakeFile()
    ffile.open()
    ffile.write("should be there")
    ffile.close()
    assert ffile.content[0] == "should be there"
    with pytest.raises(IOError):
        ffile.write("should fail")

    # Reset fake file
    ffile = FakeFile()

    with pytest.raises(IOError):
        flu(range(5)).side_effect(ffile.write).collect()

    gen_result = (
        flu(range(5))
        .side_effect(ffile.write, before=ffile.open, after=ffile.close)
        .collect()
    )
    assert ffile.is_open == False
    assert ffile.content == [0, 1, 2, 3, 4]
    assert gen_result == [0, 1, 2, 3, 4]


def test_sort():
    gen = flu(range(3, 0, -1)).sort()
    assert gen.collect() == [1, 2, 3]


def test_shuffle():
    original_order = list(range(10000))
    new_order = flu(original_order).shuffle().collect()
    assert new_order != original_order
    assert len(new_order) == len(original_order)
    assert sum(new_order) == sum(original_order)


def test_map():
    gen = flu(range(3)).map(lambda x: x + 2)
    assert gen.collect() == [2, 3, 4]


def test_rate_limit():
    resA = flu(range(3)).collect()
    resB = flu(range(3)).rate_limit(5000).collect()
    assert resA == resB


def test_map_item():
    gen = flu(range(3)).map(lambda x: {"a": x}).map_item("a")
    assert gen.collect() == [0, 1, 2]


def test_map_attr():
    class Person:
        def __init__(self, age: int) -> None:
            self.age = age

    gen = flu(range(3)).map(lambda x: Person(x)).map_attr("age")
    assert gen.collect() == [0, 1, 2]


def test_filter():
    gen = flu(range(3)).filter(lambda x: 0 < x < 2)
    assert gen.collect() == [1]


def test_take():
    gen = flu(range(10)).take(5)
    assert gen.collect() == [0, 1, 2, 3, 4]


def test_take_while():
    gen = flu(cycle(range(10))).take_while(lambda x: x < 4)
    assert gen.collect() == [0, 1, 2, 3]


def test_drop_while():
    gen = flu([1, 2, 3, 4, 3, 2, 1]).drop_while(lambda x: x < 4)
    assert gen.collect() == [4, 3, 2, 1]


def test_group_by():
    gen = flu([1, 1, 1, 2, 2, 2, 2, 3]).zip(range(100)).group_by(lambda x: x[0])
    g1, g2, g3 = gen.map(lambda x: (x[0], x[1].collect())).collect()
    # Standard usage
    assert g1 == (1, [(1, 0), (1, 1), (1, 2)])
    assert g2 == (2, [(2, 3), (2, 4), (2, 5), (2, 6)])
    assert g3 == (3, [(3, 7)])
    # No param usage
    v1 = flu(range(10)).group_by().map(lambda x: (x[0], list(x[1])))
    v2 = flu(range(10)).map(lambda x: (x, [x]))
    assert v1.collect() == v2.collect()
    # Sort
    gen = flu([1, 2, 1, 2]).group_by(lambda x: x, sort=False)
    assert gen.count() == 4
    gen = flu([1, 2, 1, 2]).group_by(lambda x: x, sort=True)
    assert gen.count() == 2

    # Identity Function
    points = [{"x": 1, "y": 0}, {"x": 4, "y": 3}, {"x": 1, "y": 5}]
    key_func = lambda u: u["x"]
    gen = flu.group_by(points, key=key_func, sort=True).collect()
    assert len(gen) == 2
    assert gen[0][0] == 1
    assert gen[1][0] == 4
    assert len(gen[0][1].collect()) == 2
    assert len(gen[1][1].collect()) == 1


def test_chunk():
    gen = flu(range(5)).chunk(2)
    assert gen.collect() == [[0, 1], [2, 3], [4]]


def test_next():
    gen = flu(range(5))
    assert next(gen) == 0


def test_iter():
    gen = flu(range(5))
    assert next(iter(gen)) == 0


def test_enumerate():
    # Check default
    gen = flu(range(3)).enumerate()
    assert gen.collect() == [(0, 0), (1, 1), (2, 2)]

    # Check start param
    gen = flu(range(3)).enumerate(start=1)
    assert gen.collect() == [(1, 0), (2, 1), (3, 2)]


def test_zip():
    gen = flu(range(3)).zip(range(3))
    assert gen.collect() == [(0, 0), (1, 1), (2, 2)]

    gen = flu(range(3)).zip(range(3), range(2))
    assert gen.collect() == [(0, 0, 0), (1, 1, 1)]


def test_zip_longest():
    gen = flu(range(3)).zip_longest(range(5))
    assert gen.collect() == [(0, 0), (1, 1), (2, 2), (None, 3), (None, 4)]
    gen = flu(range(3)).zip_longest(range(5), fill_value="a")
    assert gen.collect() == [(0, 0), (1, 1), (2, 2), ("a", 3), ("a", 4)]
    gen = flu(range(3)).zip_longest(range(5), range(4), fill_value="a")
    assert gen.collect() == [
        (0, 0, 0),
        (1, 1, 1),
        (2, 2, 2),
        ("a", 3, 3),
        ("a", 4, "a"),
    ]


def test_window():
    # Check default
    gen = flu(range(5)).window(n=3)
    assert gen.collect() == [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

    # Check step param
    gen = flu(range(5)).window(n=3, step=3)
    assert gen.collect() == [(0, 1, 2), (3, 4, None)]

    # Check fill_value param
    gen = flu(range(5)).window(n=3, step=3, fill_value="i")
    assert gen.collect() == [(0, 1, 2), (3, 4, "i")]


def test_flu():
    gen = (
        flu(count())
        .map(lambda x: x ** 2)
        .filter(lambda x: x % 517 == 0)
        .chunk(5)
        .take(3)
    )
    assert next(gen) == [0, 267289, 1069156, 2405601, 4276624]


def test_lazy():
    # TODO(or)
    pass


def test_flatten():
    nested = [1, [2, (3, [4])], ["rbsd", "abc"], (7,)]

    # Defaults with depth of 1
    gen = flu(nested).flatten()
    assert [x for x in gen] == [1, 2, (3, [4]), "rbsd", "abc", 7]

    # Depth 2
    gen = flu(nested).flatten(depth=2)
    assert [x for x in gen] == [1, 2, 3, [4], "rbsd", "abc", 7]

    # Depth 3
    gen = flu(nested).flatten(depth=3)
    assert [x for x in gen] == [1, 2, 3, 4, "rbsd", "abc", 7]

    # Depth infinite
    gen = flu(nested).flatten(depth=sys.maxsize)
    assert [x for x in gen] == [1, 2, 3, 4, "rbsd", "abc", 7]

    # Depth 2 with tuple base_type
    gen = flu(nested).flatten(depth=2, base_type=tuple)
    assert [x for x in gen] == [1, 2, (3, [4]), "rbsd", "abc", (7,)]

    # Depth 2 with iterate strings
    gen = flu(nested).flatten(depth=2, base_type=tuple, iterate_strings=True)
    assert [x for x in gen] == [1, 2, (3, [4]), "r", "b", "s", "d", "a", "b", "c", (7,)]


def test_tee():
    # Default unpacking
    gen1, gen2 = flu(range(100)).tee()
    assert gen1.sum() == gen2.sum()

    # adjusting *n* paramter
    gen1, gen2, gen3 = flu(range(100)).tee(3)
    assert gen1.sum() == gen3.sum()

    # No sync progress
    gen1, gen2 = flu(range(100)).tee()
    assert next(gen1) == next(gen2)

    # No break chaining
    assert flu(range(5)).tee().map(sum).sum() == 20
