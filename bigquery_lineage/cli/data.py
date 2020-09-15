# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from pprint import pprint
from typing import List

import click

from google.cloud import logging as cloud_logging
from google.cloud import logging_v2 as cloud_logging_v2
from google import auth

from bigquery_lineage.data.bigquery import BigQueryDataCollector


@click.group()
@click.pass_context
def data(context):
    """Commands for collecting data"""


@data.command()
@click.option("--output", type=str, required=True)
@click.option("--projects", type=str, multiple=True, required=True)
@click.option("--start", type=str, required=True, help="start data")
@click.option("--end", type=str, required=True, help="end data")
@click.option("--limit", type=int, required=False, default=100000,
              help="The maximum number of records")
@click.option("--dry_run", type=bool, help="dry run", default=False)
def logging(
        output: str,
        projects: List[str],
        start: str,
        end: str,
        limit,
        dry_run: bool):
    client = cloud_logging_v2.LoggingServiceV2Client()
    filter = '''
    protoPayload.metadata.@type = "type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"
    AND timestamp >= "{start}"
    AND timestamp <= "{end}"
    '''.format(start=start, end=end)
    entries = client.list_log_entries(
        project_ids=projects,
        resource_names=[],
        page_size=500,
        filter_=filter,
        order_by=cloud_logging.DESCENDING,
    )
    # TODO implement


@data.command()
@click.option("--output", type=str, required=True)
@click.option("--config", type=click.Path(exists=True), required=True)
@click.option("--dry_run", type=bool, help="dry run", default=False)
def bigquery(
        output: str,
        projects: List[str],
        start: str,
        end: str,
        limit,
        dry_run: bool):
    """Collect data from BigQuery."""
    collector = BigQueryDataCollector(
        output=output, projects=projects, start_date=start, end_date=end, limit=limit)
    collector.run(dry_run=dry_run)
