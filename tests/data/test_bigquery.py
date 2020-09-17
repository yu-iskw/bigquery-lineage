# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import unittest

from bigquery_lineage.data.bigquery import build_query_job_config, BigQueryDataCollector


class TestBigQueryDataCollector(unittest.TestCase):

    def test_build_query_job_config_default(self):
        job_config = build_query_job_config()
        self.assertEqual(job_config.dry_run, False)

    def test_build_query_job_config_applied(self):
        job_config = build_query_job_config(
            dry_run=True,
        )
        self.assertEqual(job_config.dry_run, True)

    def test_generate_query(self):
        project = "dummy-project-1"
        dataset = "test_dataset"
        start_date = "2020-01-01"
        end_date = "2020-01-31"
        query = BigQueryDataCollector.generate_query(
            project=project,
            dataset=dataset,
            start_date=start_date,
            end_date=end_date,
        )
        self.assertTrue(project in query)
        self.assertTrue(dataset in query)
        self.assertTrue(start_date in query)
        self.assertTrue(end_date in query)
