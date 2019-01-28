import os
from typing import Iterable

from flupy import flu


def walk_files(path: str = ".", abspath=True) -> Iterable[str]:
    """Yield files recursively starting from *path"""

    def _impl():
        for d, dirs, files in os.walk(path):
            for x in files:
                rel_path = os.path.join(d, x)
                if abspath:
                    yield os.path.abspath(rel_path)
                else:
                    yield rel_path

    return flu(_impl())


def walk_dirs(path: str = ".") -> Iterable[str]:
    """Yield files recursively starting from *path"""

    def _impl():
        for d, _, _ in os.walk(path):
            yield d

    return flu(_impl())
