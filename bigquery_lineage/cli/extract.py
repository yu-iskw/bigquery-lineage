# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import glob
import os
from typing import List

import click

from bigquery_lineage.auditlog import Auditlog
from bigquery_lineage.data.bigquery import AUDITLOG_FILE_NAME, BigQueryDataCollector


@click.command()
@click.option("--data_dir", type=str, required=True, default="./data")
def extract(
        data_dir: str):
    """Collect data"""
    files = find_auditlog_files(data_dir=data_dir)
    for file in files:
        audit_logs = BigQueryDataCollector.load_audit_logs(file)
        print(audit_logs)


def find_auditlog_files(data_dir: str) -> List[str]:
    files = glob.glob(
        os.path.join(os.path.abspath(data_dir), "**", AUDITLOG_FILE_NAME),
        recursive=True)
    return files