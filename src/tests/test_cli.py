from tempfile import NamedTemporaryFile

import pytest

from flupy.cli.cli import build_import_dict, main, parse_args


def test_parse_args():
    with pytest.raises(SystemExit) as cm:
        parse_args([])
        assert cm.exception.code == 2

    args = parse_args(["_"])
    assert args.command == "_"

    args = parse_args(["_", "-i", "os:environ:env"])
    assert "os:environ:env" in getattr(args, "import")
    assert args.command == "_"

    import_dict = build_import_dict(["json"])
    assert "json" in import_dict


def test_build_import_dict():
    import json

    import_dict = build_import_dict(["json"])
    assert "json" in import_dict
    assert import_dict["json"] == json

    import_dict = build_import_dict(["json:dumps"])
    assert "dumps" in import_dict
    assert import_dict["dumps"] == json.dumps

    import_dict = build_import_dict(["json:dumps:ds"])
    assert "ds" in import_dict
    assert import_dict["ds"] == json.dumps

    import_dict = build_import_dict(["json::j"])
    assert "j" in import_dict
    assert import_dict["j"] == json


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


def test_cli_walk_files(capsys):
    main(["flu", "walk_files().head(2)"])
    result = capsys.readouterr()
    stdout = result.out.strip("\n").split("\n")
    assert len(stdout) == 2


def test_cli_walk_dirs(capsys):
    main(["flu", "walk_dirs().head(2)"])
    result = capsys.readouterr()
    stdout = result.out.strip("\n").split("\n")
    assert len(stdout) == 2


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
