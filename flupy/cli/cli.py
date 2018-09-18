import argparse
import importlib
import sys
from signal import SIG_DFL, SIGPIPE, signal

from flupy import flu, with_iter
from flupy.cli.lazy_import import csv, json, math, os, random, re, statistics, collections, itertools
from flupy.cli.utils import walk_files, walk_folders


def read_file(filename):
    with open(filename, 'r') as f:
        yield from f

parser = argparse.ArgumentParser(description='flupy: a fluent interface for python')
parser.add_argument('command', help='flupy command to execute on input')
parser.add_argument('-f', '--file', help='path to input file')


def main():
    args = parser.parse_args()

    _command = args.command
    _file = args.file

    if _file:
        _ = flu(read_file(_file)).map(str.rstrip)
    else:
        # Do not raise exception for Broken Pipe
        signal(SIGPIPE, SIG_DFL)
        _ = flu(sys.stdin).map(str.rstrip)

    pipeline = eval(_command)

    if hasattr(pipeline, '__iter__') and not isinstance(pipeline, (str, bytes)):
        for r in pipeline:
            sys.stdout.write(str(r) + '\n')

    elif pipeline is None:
        pass
    else:
        sys.stdout.write(str(pipeline) + '\n')
