import sys

from signal import signal, SIGPIPE, SIG_DFL

from chainable import chainable


def main():
    # Do not raise exception for Broken Pipe
    signal(SIGPIPE, SIG_DFL)

    if len(sys.argv) > 2:
        sys.stdout.write("Call chainable with 1 argument, a pipeline", flush=True)
        sys.exit()

    _ = chainable(sys.stdin)

    pipeline = eval(sys.argv[1])

    if hasattr(pipeline, '__iter__'):
        for r in pipeline:
            sys.stdout.write(str(r) + '\n' + '\0')
    else:
        sys.stdout.write(str(pipeline) + '\n' + '\0')
