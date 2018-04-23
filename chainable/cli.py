from chainable import chainable
import sys

def main():
    if len(sys.argv) > 2:
        print("Call chainable with 1 argument, a pipeline", flush=True)
        sys.exit()

    _ = chainable(sys.stdin.readlines())

    for r in eval(sys.argv[1]):
        print(r)
