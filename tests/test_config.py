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
        expected = [
            ConfigFilters.ExcludedTable(project_regexp='^dummy-project-01$', dataset_regexp='^tmp_$'),
            ConfigFilters.ExcludedTable(project_regexp='^dummy-project-02$', table_regexp='^_.*$'),
        ]
        self.assertEqual(config.filters.excluded_tables, expected)
        expected = ['.*@example1.com', '.*@example2.com']
        self.assertEqual(config.filters.excluded_principal_emails, expected)


class TestConfigFilters(unittest.TestCase):

    def test_is_excluded_table(self):
        target_table_ids = [
            ("dummy-project-01", "dataset_01", "table"),
            ("dummy-project-02", "dataset_02", "table"),
            ("dummy-project-03", "dataset_03", "table"),
        ]
        excluded_tables = [
            {"project_regexp": "dummy-project-01"},
            {"dataset_regexp": "dataset_03"},
        ]
        excluded_tables = [ConfigFilters.ExcludedTable(**x) for x in excluded_tables]
        filters = ConfigFilters(excluded_tables=excluded_tables)
        result = [
            filters.is_excluded_table(project=project, dataset=dataset, table=table)
            for project, dataset, table in target_table_ids]
        expected = [True, False, True]
        self.assertEqual(result, expected)

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
