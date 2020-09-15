# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json
import os
from datetime import date, datetime

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


def load_json(path: str) -> str:
    """Load a JSON file.

    Args:
        path: path to a JSON file

    Returns:
        str: JSON string
    """
    with open(path, "r") as fp:
        return json.load(fp)


def serialize_json(obj):
    """Serialize a JSON object.

    SEE
    https://www.yoheim.net/blog.php?q=20170703
    """
    if isinstance(obj, (datetime, date)):
        # Convert to ISO format
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))
