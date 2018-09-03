#!/usr/bin/env python

"""Setup script for the package."""

import os
import sys
import logging
import setuptools


PACKAGE_NAME = 'flupy'
MINIMUM_PYTHON_VERSION = '3.5'


def check_python_version():
    """Exit when the Python version is too low."""
    if sys.version < MINIMUM_PYTHON_VERSION:
        sys.exit("Python {0}+ is required.".format(MINIMUM_PYTHON_VERSION))


def read_package_variable(key, filename='__init__.py'):
    """Read the value of a variable from the package without importing."""
    module_path = os.path.join(PACKAGE_NAME, filename)
    with open(module_path) as module:
        for line in module:
            parts = line.strip().split(' ', 2)
            if parts[:-1] == [key, '=']:
                return parts[-1].strip("'")
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
        return readme + '\n' + changelog


check_python_version()


#see http://www.niteoweb.com/blog/setuptools-run-custom-code-during-install
#This is so we can call "make" automatically during setup
class CustomInstall(install):
    def run(self):
        try:
            subprocess.call(['make'],cwd=path.join(here,'flupy'))
        except Exception as e:
            print e
            print "Error compiling t2p.c.   Try running 'make'."
            exit(1)
        else:
            install.run(self)


setuptools.setup(
    name=read_package_variable('__project__'),
    version=read_package_variable('__version__'),

    description="Method chaining built on generators",
    url='https://github.com/olirice/flupy',
    author='Oliver Rice',
    author_email='oliver@oliverrice.com',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'flu = flupy.cli.cli:main',
            ]
        },
    long_description=build_description(),
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    package_data={
        'flupy': ['Makefile']
    },
    cmdclass={'install': CustomInstall}
)
