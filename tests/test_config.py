# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import unittest

from bigquery_lineage.utils import (
    get_project_root, load_yaml
)
from bigquery_lineage.config import Config, ConfigFilters


class TestConfig(unittest.TestCase):

    def test_parse(self):
        path = os.path.join(get_project_root(), "tests", "resources", "test-config.yml")
        yaml_block = load_yaml(path)
        config = Config.parse(yaml_block)

        # test basics
        self.assertEqual(config.start, "2020-01-01")
        self.assertEqual(config.end, "2020-08-01")
        self.assertEqual(config.limit, 12345)

        # test sources
        self.assertEqual(len(config.sources), 2)
        self.assertEqual(config.sources[0].project, "gcp-project-1")
        self.assertEqual(config.sources[0].dataset, "audit_log")
        self.assertEqual(config.sources[1].project, "gcp-project-2")
        self.assertEqual(config.sources[1].dataset, "bigquery_auditlog")

        # test filters
        self.assertEqual(config.filters.excluded_tables,
                         ['.*\\.excluded_dataset_01\\..*', '.*\\.excluded_dataset_02\\..*'])
        self.assertEqual(config.filters.excluded_principal_emails,
                         ['.*@example1.com', '.*@example2.com'])


class TestConfigFilters(unittest.TestCase):

    def test_is_excluded_principal_email(self):
        target_emails = [
            "tom@example01.com",
            "tom@example02.com",
            "tom@example03.com",
        ]
        excluded_principal_emails = [
            "@example01",
            "@example03\\.com",
        ]
        filters = ConfigFilters(excluded_principal_emails=excluded_principal_emails)
        result = [
            filters.is_excluded_principal_email(email)
            for email in target_emails
        ]
        expected = [True, False, True]
        self.assertEqual(result, expected)
