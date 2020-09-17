# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import glob
import os
from typing import List

import click

from bigquery_lineage.auditlog.auditlog import read_auditlog
from bigquery_lineage.auditlog.pydot_builder import PydotBuilderV1
from bigquery_lineage.data.bigquery import AUDITLOG_FILE_NAME
from bigquery_lineage.logger import get_logger


@click.group()
@click.pass_context
# pylint: disable=unused-argument
def graph(context):
    """Commands to build a graph"""


@graph.command()
@click.option("--data_dir", type=click.Path(exists=True), required=True, default="./data")
@click.option("--output", type=str, required=True)
@click.option("--format", type=str, required=False, default="png")
def pydot(
        data_dir: str,
        output: str,
        format: str):
    """Visualize a graph with pydot."""
    logger = get_logger()

    files = find_auditlog_files(data_dir=data_dir)
    builder = PydotBuilderV1()
    for file in files:
        logger.info("Read {}".format(file))
        for auditlog in read_auditlog(file=file):
            builder.update(auditlog=auditlog)
    logger.info("Build a graph to {}".format(os.path.abspath(output)))
    graph = builder.build()
    graph.write(path=output, format=format)


def find_auditlog_files(data_dir: str) -> List[str]:
    """Find files of auditlogs."""
    files = glob.glob(
        os.path.join(os.path.abspath(data_dir), "**", AUDITLOG_FILE_NAME),
        recursive=True)
    return files