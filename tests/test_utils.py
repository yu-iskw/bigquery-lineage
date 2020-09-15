# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json
import os
import unittest
from datetime import datetime

from bigquery_lineage.utils import (
    get_project_root, serialize_json, load_json
)


class TestUtils(unittest.TestCase):

    def test_get_project_path(self):
        templates_path = get_project_root()
        self.assertTrue(os.path.isdir(templates_path))

    def test_load_json(self):
        path = os.path.join(get_project_root(), "tests", "resources", "test.json")
        result = load_json(path)
        expected = {'a': 1, 'b': {'b1': 1}}
        self.assertDictEqual(result, expected)

    def test_serialize_json(self):
        data = {"date": datetime(year=2020, month=1, day=1)}
        converted = json.dumps(data, default=serialize_json)
        result = json.loads(converted)
        self.assertEqual(result["date"], "2020-01-01T00:00:00")

