import argparse
import importlib
import sys
from signal import SIG_DFL, SIGPIPE, signal
from typing import Any, Dict, Generator, List, Optional

from flupy import __version__, flu, walk_dirs, walk_files


def read_file(path: str) -> Generator[str, None, None]:
    """Yield lines from a file given its path"""
    with open(path, "r") as f:
        yield from f


def parse_args(args: List[str]) -> argparse.Namespace:
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
        description="flupy: a fluent interface for python collections",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
    parser.add_argument("command", help="command to execute against input")
    parser.add_argument("-f", "--file", help="path to input file")
    parser.add_argument(
        "-i",
        "--import",
        nargs="*",
        default=[],
        help="modules to import\n"
        "Syntax: <module>:<object>:<alias>\n"
        "Examples:\n"
        "\t'import os' = '-i os'\n"
        "\t'import os as op_sys' = '-i os::op_sys'\n"
        "\t'from os import environ' = '-i os:environ'\n"
        "\t'from os import environ as env' = '-i os:environ:env'\n",
    )
    return parser.parse_args(args)


def build_import_dict(imps: List[str]) -> Dict[str, Any]:
    """Execute CLI scoped imports"""
    import_dict = {}
    for imp_stx in imps:
        module, _, obj_alias = imp_stx.partition(":")
        obj, _, alias = obj_alias.partition(":")

        if not obj:
            import_dict[alias or module] = importlib.import_module(module)
        else:
            _garb = importlib.import_module(module)
            import_dict[alias or obj] = getattr(_garb, obj)
    return import_dict


def main(argv: Optional[List[str]] = None) -> None:
    """CLI Entrypoint"""
    args = parse_args(argv[1:] if argv is not None else sys.argv[1:])

    _command = args.command
    _file = args.file
    _import = getattr(args, "import")

    import_dict = build_import_dict(_import)

    if _file:
        _ = flu(read_file(_file)).map(str.rstrip)
    else:
        # Do not raise exception for Broken Pipe
        signal(SIGPIPE, SIG_DFL)
        _ = flu(sys.stdin).map(str.rstrip)

    locals_dict = {
        "flu": flu,
        "_": _,
        "walk_files": walk_files,
        "walk_dirs": walk_dirs,
    }

    pipeline = eval(_command, import_dict, locals_dict)

    if hasattr(pipeline, "__iter__") and not isinstance(pipeline, (str, bytes)):
        for r in pipeline:
            sys.stdout.write(str(r) + "\n")

    elif pipeline is None:
        pass
    else:
        sys.stdout.write(str(pipeline) + "\n")
