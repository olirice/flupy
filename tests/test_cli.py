import sys
from tempfile import NamedTemporaryFile

import pytest

from flupy.cli.cli import execute_imports, main, parse_args


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


def test_show_help(capsys):
    with pytest.raises(SystemExit):
        main(["flu", "-h"])

    result = capsys.readouterr()
    stdout = result.out
    assert stdout.startswith("usage")


def test_show_version(capsys):
    main(["flu", "flu(range(5)).collect()"])

    result = capsys.readouterr()
    stdout = result.out.replace("\n", "")
    assert stdout.startswith("0")


def test_basic_pipeline(capsys):
    main(["flu", "flu(range(5)).collect()"])
    result = capsys.readouterr()
    stdout = result.out.replace("\n", "")
    assert stdout.startswith("0")


def test_pass_on_none_pipeline(capsys):
    main(["flu", "None"])
    result = capsys.readouterr()
    stdout = result.out
    assert stdout == ""


def test_non_iterable_non_none_pipeline(capsys):
    main(["flu", '"hello_world"'])
    result = capsys.readouterr()
    stdout = result.out.strip("\n")
    assert stdout == "hello_world"


def test_from_file(capsys):
    with NamedTemporaryFile("w+") as f:
        f.write("hello")
        f.read()
        f_name = f.name
        main(["flu", "-f", f_name, "_.map(str.upper)"])
    result = capsys.readouterr()
    stdout = result.out.strip("\n")
    assert stdout == "HELLO"


def test_glob_imports(capsys):
    main(["flu", "flu(env).count()", "-i", "os:environ:env"])
    result = capsys.readouterr()
    stdout = result.out
    assert stdout
