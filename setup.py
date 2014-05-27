#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup
from setuptools import Command
import sys


class Tox(Command):

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # import here since we just installed it
        import tox
        errno = tox.cmdline([])
        sys.exit(errno)


setup(
    name='indently',
    version='0.0.1',
    author='Bryce Lampe',
    description='Tool to automatically format Python code..',
    packages=['indently'],
    scripts=['bin/indently'],
    requires=[],
    tests_require=[
        'tox',
    ],
    cmdclass={'test': Tox},
)
