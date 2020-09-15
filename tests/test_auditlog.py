# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import unittest

from bigquery_lineage.auditlog import Auditlog
from bigquery_lineage.utils import (
    get_project_root, load_json
)


class TestAuditLog(unittest.TestCase):

    def test_job_completed_event_load(self):
        path = os.path.join(get_project_root(), "tests", "resources",
                            "auditlog", "job_completed_event", "load.json")
        block = load_json(path)
        auditlog = Auditlog.parse(block=block)
        # methodName
        self.assertEqual(auditlog.protopayload_auditlog.methodName, "jobservice.jobcompleted")
        # sourceUris
        result = (auditlog.protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent
                   .jobConfiguration.load.sourceUris)
        expected = [
            'gs://datalake/spanner/dag_name=dag1/task_id=ScheduledRepaymentSettings/year=2020/month=8/day=1/hour=0/20200801000000-*.avro',
            'gs://datalake/spanner/dag_name=dag1/task_id=ScheduledRepaymentSettings/year=2020/month=8/day=1/hour=0/20200801000000-*.snappy',
        ]
        self.assertEqual(result, expected)
        # destinationTable
        result = (auditlog.protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent
                  .jobConfiguration.load.destinationTable)
        self.assertEqual(result.project, "dummy-project")
        self.assertEqual(result.dataset, "service")
        self.assertEqual(result.table, "table")

    def test_job_completed_event_query(self):
        path = os.path.join(get_project_root(), "tests", "resources",
                            "auditlog", "job_completed_event", "query.json")
        block = load_json(path)
        auditlog = Auditlog.parse(block=block)
        # methodName
        self.assertEqual(auditlog.protopayload_auditlog.methodName, "jobservice.jobcompleted")
        # referencedTables
        result = (auditlog.protopayload_auditlog.servicedata_v1_bigquery
                  .jobCompletedEvent.jobStatistics.referencedTables)
        self.assertEqual(result[0].project, "dummy-project")
        self.assertEqual(result[0].dataset, "data_quality")
        self.assertEqual(result[0].table, "table1")
        # destinationTable
        result = (auditlog.protopayload_auditlog.servicedata_v1_bigquery.jobCompletedEvent
                  .jobConfiguration.query.destinationTable)
        self.assertEqual(result.project, "dummy-project")
        self.assertEqual(result.dataset, "destination_dataset")
        self.assertEqual(result.table, "destination_table")
