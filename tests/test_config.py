# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import unittest

from bigquery_lineage.utils import (
    get_project_root, load_yaml
)
from bigquery_lineage.config import Config


class TestConfig(unittest.TestCase):

    def test_parse(self):
        path = os.path.join(get_project_root(), "tests", "resources", "test-config.yml")
        yaml_block = load_yaml(path)
        config = Config.parse(yaml_block)
        self.assertEqual(config.start, "2020-01-01")
        self.assertEqual(config.end, "2020-08-01")
        self.assertEqual(config.limit, 12345)
        self.assertEqual(len(config.sources), 2)
        self.assertEqual(config.sources[0].project, "gcp-project-1")
        self.assertEqual(config.sources[0].dataset, "audit_log")
        self.assertEqual(config.sources[1].project, "gcp-project-2")
        self.assertEqual(config.sources[1].dataset, "bigquery_auditlog")
