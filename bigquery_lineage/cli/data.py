# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import click

#from google.cloud import logging_v2 as cloud_logging_v2

from bigquery_lineage.config import Config
from bigquery_lineage.data.bigquery import BigQueryDataCollector
from bigquery_lineage.utils import load_yaml


@click.group()
@click.pass_context
# pylint: disable=unused-argument
def data(context):
    """Commands for collecting data"""


# @data.command()
# @click.option("--output", type=str, required=True)
# @click.option("--projects", type=str, multiple=True, required=True)
# @click.option("--start", type=str, required=True, help="start data")
# @click.option("--end", type=str, required=True, help="end data")
# @click.option("--limit", type=int, required=False, default=100000,
#               help="The maximum number of records")
# @click.option("--dry_run", type=bool, help="dry run", default=False)
# def logging(
#         output: str,
#         projects: List[str],
#         start: str,
#         end: str,
#         limit,
#         dry_run: bool):
#     client = cloud_logging_v2.LoggingServiceV2Client()
#     filter = '''
#     protoPayload.metadata.@type = "type.googleapis.com/google.cloud.audit.BigQueryAuditMetadata"
#     AND timestamp >= "{start}"
#     AND timestamp <= "{end}"
#     '''.format(start=start, end=end)
#     entries = client.list_log_entries(
#         project_ids=projects,
#         resource_names=[],
#         page_size=500,
#         filter_=filter,
#         order_by=cloud_logging.DESCENDING,
#     )
#     # TODO implement


@data.command()
@click.option("--output", type=str, required=True)
@click.option("--config", type=click.Path(exists=True), required=True)
@click.option("--dry_run", type=bool, help="dry run", default=False)
def bigquery(
        output: str,
        config: str,
        dry_run: bool):
    """Collect data from BigQuery."""
    yaml_block = load_yaml(config)
    bql_config = Config.parse(yaml=yaml_block)
    collector = BigQueryDataCollector(output=output, bql_config=bql_config)
    collector.export_logs(dry_run=dry_run)
