import argparse
import importlib
import sys
from signal import SIG_DFL, SIGPIPE, signal

from typing import List

from flupy import flu, with_iter, __version__
from flupy.cli.utils import walk_dirs, walk_files


def read_file(filename):
    with open(filename, "r") as f:
        yield from f

def parse_args(args: List[str]):
    """Parse input arguments"""
    parser = argparse.ArgumentParser(
            description="flupy: a fluent interface for python",
            formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument("command", help="command to execute against input")
    parser.add_argument("-f", "--file", help="path to input file")
    parser.add_argument(
            "-i",
            "--import",
            nargs="*",
            default=[],
            help="modules to import\n" \
                 "Syntax: <module>:<object>:<alias>\n" \
                 "Examples:\n" \
                 "\t'import os' = '-i os'\n" \
                 "\t'import os as op_sys' = '-i os::op_sys'\n" \
                 "\t'from os import environ' = '-i os:environ'\n" \
                 "\t'from os import environ as env' = '-i os:environ:env'\n"
                 )
    return parser.parse_args(args)

def execute_imports(imps: List[str]):
    """Execute global imports"""
    for imp_stx in imps:
        module, _, obj_alias = imp_stx.partition(':')
        obj, _, alias = obj_alias.partition(':')
        if not obj:
            globals()[alias or module] = importlib.import_module(module)
        else:
            _garb = importlib.import_module(module)
            globals()[alias or obj] = getattr(_garb, obj)


def main():
    args = parse_args(sys.argv[1:])

    _command = args.command
    _file = args.file
    _import = getattr(args, 'import')

    execute_imports(_import)

    if _file:
        _ = flu(read_file(_file)).map(str.rstrip)
    else:
        # Do not raise exception for Broken Pipe
        signal(SIGPIPE, SIG_DFL)
        _ = flu(sys.stdin).map(str.rstrip)

    pipeline = eval(_command)

    if hasattr(pipeline, "__iter__") and not isinstance(pipeline, (str, bytes)):
        for r in pipeline:
            sys.stdout.write(str(r) + "\n")

    elif pipeline is None:
        pass
    else:
        sys.stdout.write(str(pipeline) + "\n")
