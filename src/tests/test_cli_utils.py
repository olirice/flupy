from flupy.cli.utils import walk_dirs, walk_files


def test_walk_files():
    assert walk_files().head()
    assert walk_files(abspath=False).head()


def test_walk_dirs():
    assert walk_dirs().head()
