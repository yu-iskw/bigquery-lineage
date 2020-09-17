# -*- coding: utf-8 -*-
# pylint: disable=logging-format-interpolation
from __future__ import absolute_import, division, print_function

import glob
import os
from typing import List

import click

from bigquery_lineage.auditlog.auditlog import read_auditlog
from bigquery_lineage.auditlog.pydot_builder import PydotBuilderV1
from bigquery_lineage.config import Config
from bigquery_lineage.data.bigquery import AUDITLOG_FILE_NAME
from bigquery_lineage.logger import get_logger


@click.group()
@click.pass_context
# pylint: disable=unused-argument
def graph(context):
    """Commands to build a graph"""


@graph.command()
@click.option("--data_dir", type=click.Path(exists=True), required=True, default="./data")
@click.option("--config", type=click.Path(exists=True), required=True)
@click.option("--output", type=str, required=True)
@click.option("--fmt", type=str, required=False, default="png")
def pydot(
        data_dir: str,
        config: str,
        output: str,
        fmt: str):
    """Visualize a graph with pydot."""
    logger = get_logger()

    bql_config = Config.load(path=config)
    files = find_auditlog_files(data_dir=data_dir)
    builder = PydotBuilderV1(config=bql_config)
    for file in files:
        logger.info("Read {}".format(file))
        for auditlog in read_auditlog(file=file):
            builder.update(auditlog=auditlog)
    logger.info("Build a graph to {}".format(os.path.abspath(output)))
    g = builder.build()
    g.write(path=output, format=fmt)


def find_auditlog_files(data_dir: str) -> List[str]:
    """Find files of auditlogs."""
    files = glob.glob(
        os.path.join(os.path.abspath(data_dir), "**", AUDITLOG_FILE_NAME),
        recursive=True)
    return files
