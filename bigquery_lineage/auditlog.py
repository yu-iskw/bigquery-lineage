# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function


from google.cloud import bigquery


class Auditlog:

    def __init__(self):
        pass

    @classmethod
    def from_bigquery_row(cls, row: bigquery.Row):
        referenced_tables = row.protopayload_auditlog.servicedata_v1_bigquery.jobInsertResponse.jobStatistics.referencedTables
