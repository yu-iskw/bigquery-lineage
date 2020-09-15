# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from typing import List

import click

from bigquery_lineage.data.bigquery import BigQueryDataCollector


@click.command()
@click.pass_context
@click.option("--output", type=str, required=True)
@click.option("--projects", type=str, multiple=True, required=True)
@click.option("--start", type=str, required=True, help="start data")
@click.option("--end", type=str, required=True, help="end data")
@click.option("--limit", type=int, required=False, default=100000,
              help="The maximum number of records")
@click.option("--dry_run", type=bool, help="dry run", default=False)
def data(
        context,
        output: str,
        projects: List[str],
        start: str,
        end: str,
        limit,
        dry_run: bool):
    collector = BigQueryDataCollector(
        output=output, projects=projects, start_date=start, end_date=end, limit=limit)
    collector.run(dry_run=dry_run)
