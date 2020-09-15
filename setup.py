#!/usr/bin/env python

import sys

import bigquery_lineage
from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='bigquery-lineage',
    version=bigquery_lineage.VERSION,
    packages=find_packages(),
    install_requires=[
        "click==7.1.2",
        "click-completion==0.5.2",
        "google-cloud-bigquery>=1.26.0",
        "dictdiffer==0.8.1",
        "Jinja2>=2.11",
    ],
    entry_points={
        "console_scripts": [
            "bql = bigquery_lineage.cli.main:cli",
        ],
    },
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
