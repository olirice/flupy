import sys

import pytest

from flupy.cli.cli import execute_imports, parse_args


def test_parse_args():
    with pytest.raises(SystemExit) as cm:
        parse_args([])
        assert cm.exception.code == 2

    args = parse_args(["_"])
    assert args.command == "_"

    args = parse_args(["_", "-i", "os:environ:env"])
    assert "os:environ:env" in getattr(args, "import")
    assert args.command == "_"

    with pytest.raises(NameError):
        json  # type: ignore

    execute_imports(["json"])
    assert "json" in sys.modules
