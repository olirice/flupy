from importlib.metadata import version

from flupy.cli.utils import walk_dirs, walk_files
from flupy.fluent import flu

__project__ = "flupy"
__version__ = version(__project__)

__all__ = ["flu", "walk_files", "walk_dirs"]
