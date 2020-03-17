============
Command Line
============


The flupy CLI is a platform agnostic application that give full access to the flupy API and python from your shell.

.. automodule:: flupy

Usage
=====

::

	$ flu -h

	usage: flu [-h] [-v] [-f FILE] [-i [IMPORT [IMPORT ...]]] command

	flupy: a fluent interface for python

	positional arguments:
	  command               command to execute against input

	optional arguments:
	  -h, --help            show this help message and exit
	  -v, --version         show program's version number and exit
	  -f FILE, --file FILE  path to input file
	  -i [IMPORT [IMPORT ...]], --import [IMPORT [IMPORT ...]]
							modules to import
							Syntax: <module>:<object>:<alias>


Basic Examples
==============

When input data are provided to the `flu` command, an instance of the Fluent/flu object is preprepared with that input and stored in the the variable `_`.


.. note:: for more information on writing flupy commands, see API Reference

Piping from another command (stdin)
-----------------------------------
Example: Show lines of a log file that are errors::

    $ cat logs.txt | flu '_.filter(lambda x: x.starswith("ERROR"))'

Reading from a file
-------------------
Example: Show lines of a log file that are errors::

    $ flu -f logs.txt '_.filter(lambda x: x.starswith("ERROR"))'

No Input data
-------------
flupy does not require input data if it can be generated from within python e.g. with `range(10)`. When no input data are provided, iterable at the beginning of the flupy command must be wraped into a Fluent/flu instance.

Example: Even integers less than 10::

    $ flu 'flu(range(10)).filter(lambda x: x%2==0)'

Import System
=============

Passing `-i` or `--import` to the cli allows you to import standard and third party libraries installed in the same environment.

Import syntax

        -i <module>:<object>:<alias>


.. note:: for multiple imports pass `-i` multiple times

Import Examples
---------------
**import os**::

    $ flu 'flu(os.environ)' -i os

**from os import environ**::

    $ flu 'flu(environ)' -i os:environ

**from os import environ as env**::

    $ flu 'flu(env)' -i os:environ:env

**import os as opsys**::

    $ flu 'flu(opsys.environ)' -i os::opsys


