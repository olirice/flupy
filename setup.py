#!/usr/bin/env python

"""Setup script for the package."""

import logging
import os
import sys

import setuptools

PACKAGE_NAME = "flupy"
MINIMUM_PYTHON_VERSION = (3, 6, 0, "", 0)


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version_info < MINIMUM_PYTHON_VERSION:
        sys.exit("At least Python {0}.{1}.{2} is required.".format(*MINIMUM_PYTHON_VERSION[:3]))


def read_package_variable(key, filename="__init__.py"):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join("src", PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(" ", 2)
            if parts[:-1] == [key, "="]:
                return parts[-1].strip("'").strip('"')
    logging.warning("'%s' not found in '%s'", key, module_path)
    return None


def build_description():
    """Build a description for the project from documentation files."""
    try:
        readme = open("README.rst").read()
        changelog = open("CHANGELOG.rst").read()
    except IOError:
        return "<placeholder>"
    else:
        return readme + "\n" + changelog


check_python_version()


DEV_REQUIRES = [
    "pytest",
    "pytest-cov",
    "pytest-benchmark",
    "pre-commit",
    "pylint",
    "black",
    "mypy",
]


ext_modules = []

if os.environ.get("MYPYC_COMPILE", False):
    from mypyc.build import mypycify

    ext_modules = mypycify(
        [
            "src/flupy/fluent.py",
            "src/flupy/cli/utils.py",
            "src/flupy/cli/cli.py",
        ],
        opt_level="3",
    )

setuptools.setup(
    name=read_package_variable("__project__"),
    version=read_package_variable("__version__"),
    description="Method chaining built on generators",
    url="https://github.com/olirice/flupy",
    author="Oliver Rice",
    author_email="oliver@oliverrice.com",
    ext_modules=ext_modules,
    packages=setuptools.find_packages("src", exclude=("src/tests",)),
    package_dir={"": "src"},
    package_data={
        "": ["py.typed"]
    },  # Allows to be analyzed by mypy when installed https://mypy.readthedocs.io/en/stable/installed_packages.html#installed-packages
    # include_package_data=True,
    entry_points={
        "console_scripts": [
            "flu = flupy.cli.cli:main",
            "flu_precommit = flupy.cli.cli:precommit",
        ]
    },
    long_description=build_description(),
    tests_require=["pytest", "coverage"],
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["typing_extensions"],
    extras_require={"dev": DEV_REQUIRES},
)
