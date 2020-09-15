# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import difflib
import re
import os
import glob
from typing import Optional, Union, List, Dict


def get_project_root() -> str:
    """Get the root path of the module."""
    return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
