import unittest
import sys
from itertools import count, cycle
from chainable import chainable
import chainable as cha

class TestChainable(unittest.TestCase):

    def test_collect(self):
        assert chainable(range(3)).collect() == [0, 1, 2]
        assert chainable(range(3)).collect(container_type=tuple) == (0, 1, 2)
        assert chainable(range(3)).collect(n=2) == [0, 1]
 
    def test_sum(self):
        gen = chainable(range(3))
        assert gen.sum() == 3

    def test_count(self):
        gen = chainable(range(3))
        assert gen.count() == 3

    def test_min(self):
        gen = chainable(range(3))
        assert gen.min() == 0

    def test_max(self):
        gen = chainable(range(3))
        assert gen.max() == 2

    def test_sort(self):
        gen = chainable(range(3, 0, -1)).sort()
        assert gen.collect() == [1, 2, 3]

    def test_map(self):
        gen = chainable(range(3)).map(lambda x: x+2)
        assert gen.collect() == [2, 3, 4]

    def test_map_item(self):
        gen = chainable(range(3)).map(lambda x: {'a': x}).map_item('a')
        assert gen.collect() == [0, 1, 2]

    def test_map_attr(self):
        class Person:
            def __init__(self, age: int):
                self.age = age

        gen = chainable(range(3)).map(lambda x: Person(x)).map_attr('age')
        assert gen.collect() == [0, 1, 2]

    def test_filter(self):
        gen = chainable(range(3)).filter(lambda x: 0 < x < 2)
        assert gen.collect() == [1]

    def test_take(self):
        gen = chainable(range(10)).take(5)
        assert gen.collect() == [0, 1, 2, 3, 4]

    def test_takewhile(self):
        gen = chainable(cycle(range(10))).takewhile(lambda x: x < 4) 
        assert gen.collect() == [0, 1, 2, 3]

    def test_dropwhile(self):
        gen = chainable([1,2,3,4,3,2,1]).dropwhile(lambda x: x < 4) 
        assert gen.collect() == [4, 3, 2, 1]
        
    def test_groupby(self):
        gen = chainable([1, 1, 1, 2, 2, 2, 2, 3]).zip(range(100)).groupby(lambda x: x[0]) 
        g1, g2, g3 = gen.map(lambda x: (x[0], x[1].collect())).collect()
        # Standard usage
        assert g1 == (1, [(1, 0), (1, 1), (1, 2)])
        assert g2 == (2, [(2, 3), (2, 4), (2, 5), (2, 6)])
        assert g3 == (3, [(3, 7)])
        # No param usage
        v1 = chainable(range(10)).groupby().map(lambda x: (x[0], list(x[1])))
        v2 = chainable(range(10)).map(lambda x: (x, [x]))
        assert v1.collect() == v2.collect()

    def test_slice(self):
        gen = chainable([1,2,3,4,3,2,1]).dropwhile(lambda x: x < 4) 
        assert gen.collect() == [4, 3, 2, 1]

    def test_chunk(self):
        gen = chainable(range(5)).chunk(2)
        assert gen.collect() == [[0, 1], [2, 3], [4]]

    def test_next(self):
        gen = chainable(range(5))
        assert next(gen) == 0
        
    def test_iter(self):
        gen = chainable(range(5))
        assert next(iter(gen)) == 0

    def test_enumerate(self):
        # Check default
        gen = chainable(range(3)).enumerate()
        assert gen.collect() == [(0, 0), (1, 1), (2, 2)]

        # Check start param
        gen = chainable(range(3)).enumerate(start=1)
        assert gen.collect() == [(1, 0), (2, 1), (3, 2)]

    def test_zip(self):
        gen = chainable(range(3)).zip(range(3))
        assert gen.collect() == [(0, 0), (1, 1), (2, 2)]

    def test_zip_longest(self):
        gen = chainable(range(3)).zip_longest(range(5))
        assert gen.collect() == [(0, 0), (1, 1), (2, 2), (None, 3), (None, 4)]
        gen = chainable(range(3)).zip_longest(range(5), fillvalue='a')
        assert gen.collect() == [(0, 0), (1, 1), (2, 2), ('a', 3), ('a', 4)]

    def test_window(self):
        # Check default
        gen = chainable(range(5)).window(n=3)
        assert gen.collect() == [(0, 1, 2), (1, 2, 3), (2, 3, 4)]

        # Check step param
        gen = chainable(range(5)).window(n=3, step=3)
        assert gen.collect() == [(0, 1, 2), (3, 4, None)]

        # Check fill_value param
        gen = chainable(range(5)).window(n=3, step=3, fill_value='i')
        assert gen.collect() == [(0, 1, 2), (3, 4, 'i')]

    def test_chainable(self):
        gen = chainable(count()) \
                .map(lambda x: x**2) \
                .filter(lambda x: x % 517 == 0) \
                .chunk(5) \
                .take(3)
        assert next(gen) == [0, 267289, 1069156, 2405601, 4276624] 

    def test_lazy(self):
        #TODO(or)
        pass

    def test_flatten(self):
        nested = [1, [2, (3, [4])], ['rbsd', 'abc'], (7,)]

        # Defaults with depth of 1
        gen = chainable(nested).flatten()
        assert [x for x in gen] == [1, 2, (3, [4]), 'rbsd', 'abc', 7]

        # Depth 2
        gen = chainable(nested).flatten(depth=2)
        assert [x for x in gen] == [1, 2, 3, [4], 'rbsd', 'abc', 7] 
        
        # Depth 3
        gen = chainable(nested).flatten(depth=3)
        assert [x for x in gen] == [1, 2, 3, 4, 'rbsd', 'abc', 7]

        # Depth infinite
        gen = chainable(nested).flatten(depth=sys.maxsize)
        assert [x for x in gen] == [1, 2, 3, 4, 'rbsd', 'abc', 7]

        # Depth 2 with tuple base_type
        gen = chainable(nested).flatten(depth=2, base_type=tuple)
        assert [x for x in gen] == [1, 2, (3, [4]), 'rbsd', 'abc', (7,)]

        # Depth 2 with iterate strings 
        gen = chainable(nested).flatten(depth=2, base_type=tuple, iterate_strings=True)
        assert [x for x in gen] == [1, 2, (3, [4]), 'r', 'b', 's', 'd', 'a', 'b', 'c', (7,)]


if __name__ == '__main__':
    uniittest.main()
