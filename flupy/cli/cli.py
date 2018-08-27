import importlib
import sys

from signal import signal, SIGPIPE, SIG_DFL

from flupy import flu 
from flupy.cli.utils import LazyObject


lazy_modules = ['json', 'os', 'csv', 're', 'math', 'random', 'statistics']
for module in lazy_modules:
    locals()[module] = LazyObject(load=lambda : importlib.import_module('os'),
                                  ctx=globals(),
                                  name='os')


def main():
    # Do not raise exception for Broken Pipe
    signal(SIGPIPE, SIG_DFL)

    if len(sys.argv) > 2:
        sys.stdout.write("Call chainable with 1 argument, a pipeline", flush=True)
        sys.exit()

    _ = flu(sys.stdin).map(str.rstrip)

    pipeline = eval(sys.argv[1])

    if hasattr(pipeline, '__iter__'):
        for r in pipeline:
            sys.stdout.write(str(r) + '\n')
    else:
        sys.stdout.write(str(pipeline) + '\n')
