# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os

import yaml


def get_project_root() -> str:
    """Get the root path of the module."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def load_yaml(path: str) -> str:
    """Load a YAML file

    Args:
        path (str): path to a YAML file

    Returns:
        dict: YAML block
    """
    with open(path, "r") as f:
        schema_source = yaml.safe_load(f.read())
        return schema_source
