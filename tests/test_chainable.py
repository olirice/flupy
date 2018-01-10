import unittest
import sys
from itertools import count
from chainable import chainable


class TestChainable(unittest.TestCase):

    def test_map(self):
        gen = chainable(range(3)).map(lambda x: x+2)
        collected = [x for x in gen]
        assert collected == [2, 3, 4]

    def test_filter(self):
        gen = chainable(range(3)).filter(lambda x: 0 < x < 2)
        collected = [x for x in gen]
        assert collected == [1]

    def test_take(self):
        gen = chainable(range(10)).take(5)
        collected = [x for x in gen]
        assert collected == [0, 1, 2, 3, 4]

    def test_chunk(self):
        gen = chainable(range(5)).chunk(2)
        collected = [x for x in gen]
        assert collected == [[0, 1], [2, 3], [4]]

    def test_next(self):
        gen = chainable(range(5))
        assert next(gen) == 0
        
    def test_iter(self):
        gen = chainable(range(5))
        assert next(iter(gen)) == 0

    def test_chainable(self):
        gen = chainable(count()) \
                .map(lambda x: x**2) \
                .filter(lambda x: x % 517 == 0) \
                .chunk(5) \
                .take(3)
        assert next(gen) == [0, 267289, 1069156, 2405601, 4276624] 

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
