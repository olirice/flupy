import sys
import unittest
from itertools import count, cycle

from flupy import as_flu, flu
from flupy.cli.cli import parse_args, execute_imports


class TestCLI(unittest.TestCase):

    def test_parse_args(self):
        with self.assertRaises(SystemExit) as cm:
            parse_args([])
        assert cm.exception.code == 2

        args = parse_args(["_"])
        assert args.command == '_'

        args = parse_args(["_", "-i", "os:environ:env"])
        assert "os:environ:env" in getattr(args, 'import')
        assert args.command == '_'

        with self.assertRaises(NameError):
            json

        execute_imports(['json'])
        assert 'json' in sys.modules

if __name__ == '__main__':
    uniittest.main()
