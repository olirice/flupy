from flupy import flu
from flupy.cli.utils import walk_dirs, walk_files


def test_walk_files():
    assert walk_files().head()
    assert walk_files(abspath=False).head()


def test_walk_dirs():
    assert walk_dirs().head()


# Edge case tests


def test_walk_files_returns_fluent():
    """walk_files() should return a Fluent object."""
    result = walk_files()
    assert isinstance(result, flu)


def test_walk_dirs_returns_fluent():
    """walk_dirs() should return a Fluent object."""
    result = walk_dirs()
    assert isinstance(result, flu)


def test_walk_files_empty_directory(tmp_path):
    """walk_files() on empty directory should return empty."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    result = walk_files(str(empty_dir)).collect()
    assert result == []


def test_walk_dirs_empty_directory(tmp_path):
    """walk_dirs() on directory with no subdirs returns root only."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    result = walk_dirs(str(empty_dir)).collect()
    # walk_dirs includes the root directory itself
    assert len(result) == 1
    assert str(empty_dir) in result[0]
