from flupy import flu


def test_integration(benchmark):
    @benchmark
    def work():
        (flu(range(100000)).chunk(100).chunk(2).map_item(0).count())


def test_max(benchmark):
    @benchmark
    def work():
        flu(range(300000)).max()


def test_initialize(benchmark):
    @benchmark
    def work():
        flu(range(10))


def test_collect(benchmark):
    @benchmark
    def work():
        flu(range(3)).collect()


def test___getitem__(benchmark):
    @benchmark
    def work():
        flu(range(350))[1:3].collect()


def test_sum(benchmark):
    @benchmark
    def work():
        gen = flu(range(1000)).sum()


def test_reduce(benchmark):
    @benchmark
    def work():
        flu(range(50)).reduce(lambda x, y: x + y)


def test_fold_left(benchmark):
    @benchmark
    def work():
        flu(range(5)).fold_left(lambda x, y: x + y, 0)


def test_count(benchmark):
    @benchmark
    def work():
        gen = flu(range(3000)).count()


def test_min(benchmark):
    @benchmark
    def work():
        flu(range(3000)).min()


def test_first(benchmark):
    @benchmark
    def work():
        flu(range(3)).first()


def test_last(benchmark):
    @benchmark
    def work():
        flu(range(3000)).last()


def test_head(benchmark):
    @benchmark
    def work():
        flu(range(30000)).head(n=10)


def test_tail(benchmark):
    @benchmark
    def work():
        gen = flu(range(30000)).tail(n=10)


def test_unique(benchmark):
    class NoHash:
        def __init__(self, letter, keyf):
            self.letter = letter
            self.keyf = keyf

    a = NoHash("a", 1)
    b = NoHash("b", 1)
    c = NoHash("c", 2)

    data = [x % 500 for x in range(10000)]

    @benchmark
    def work():
        gen = flu(data).unique().collect()


def test_sort(benchmark):
    @benchmark
    def work():
        flu(range(3000, 0, -1)).sort().collect()


def test_shuffle(benchmark):
    original_order = list(range(10000))

    @benchmark
    def work():
        flu(original_order).shuffle().collect()


def test_map(benchmark):
    @benchmark
    def work():
        flu(range(3)).map(lambda x: x + 2).collect()


def test_rate_limit(benchmark):
    @benchmark
    def work():
        flu(range(300)).rate_limit(50000000000000).collect()


def test_map_item(benchmark):
    data = flu(range(300)).map(lambda x: {"a": x})

    @benchmark
    def work():
        gen = flu(data).map_item("a")


def test_map_attr(benchmark):
    class Person:
        def __init__(self, age: int) -> None:
            self.age = age

    people = flu(range(200)).map(Person).collect()

    @benchmark
    def work():
        flu(people).map_attr("age").collect()


def test_filter(benchmark):
    @benchmark
    def work():
        flu(range(3)).filter(lambda x: 0 < x < 2).collect()


def test_take(benchmark):
    @benchmark
    def work():
        flu(range(10)).take(5).collect()


def test_take_while(benchmark):
    @benchmark
    def work():
        flu(cycle(range(10))).take_while(lambda x: x < 4).collect()


def test_drop_while(benchmark):
    @benchmark
    def work():
        flu([1, 2, 3, 4, 3, 2, 1]).drop_while(lambda x: x < 4).collect()


def test_group_by(benchmark):
    @benchmark
    def work():
        flu([1, 1, 1, 2, 2, 2, 2, 3]).zip(range(100)).group_by(lambda x: x[0]).collect()


def test_chunk(benchmark):
    @benchmark
    def work():
        flu(range(500)).chunk(2).collect()


def test_enumerate(benchmark):
    @benchmark
    def work():
        flu(range(3)).enumerate(start=1).collect()


def test_zip(benchmark):
    @benchmark
    def work():
        flu(range(3)).zip(range(3)).collect()


def test_zip_longest(benchmark):
    @benchmark
    def work():
        flu(range(3)).zip_longest(range(5)).collect()


def test_window(benchmark):
    @benchmark
    def work():
        gen = flu(range(5)).window(n=3, step=3).collect


def test_flatten(benchmark):
    nested = [1, [2, (3, [4])], ["rbsd", "abc"], (7,)]

    @benchmark
    def work():
        gen = flu(nested).flatten(depth=2, base_type=tuple).collect()


def test_tee(benchmark):
    @benchmark
    def work():
        gen1, gen2, gen3 = flu(range(100)).tee(3)


def test_join_left(benchmark):
    @benchmark
    def work():
        flu(range(6)).join_left(range(0, 6, 2)).collect()


def test_join_inner(benchmark):
    @benchmark
    def work():
        flu(range(6)).join_inner(range(0, 6, 2)).collect()
