# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import json
import os
import pickle
from typing import List

import jinja2
from google.cloud import bigquery

from bigquery_lineage.config import Config
from bigquery_lineage.logger import get_logger
from bigquery_lineage.utils import serialize_json

AUDITLOG_FILE_NAME = "auditlog.json"


def build_query_job_config(**kwargs) -> bigquery.QueryJobConfig:
    """Build bigquery.QueryJobConfig."""
    default = {
        "dry_run": False,
        "allow_large_results": True,
        "use_legacy_sql": False,
        "use_query_cache": True,
    }
    job_config_params = {**default, **kwargs}
    job_config = bigquery.QueryJobConfig(**job_config_params)
    return job_config


class BigQueryDataCollector:

    def __init__(self,
                 output: str,
                 bql_config: Config,
                 job_config: bigquery.QueryJobConfig = build_query_job_config()):
        self._output = output
        self._bql_config = bql_config
        self._job_config = job_config

    def export_logs(self, dry_run: bool = True) -> None:
        """Export BigQuery audit logs to files respectively
        The outputs are files. Each file contains audit logs in a GCP project.
        """
        logger = get_logger()

        for source in self._bql_config.sources:
            project = source.project
            dataset = source.dataset
            query = self.generate_query(
                project=project,
                dataset=dataset,
                start_date=self._bql_config.start,
                end_date=self._bql_config.end,
                limit=self._bql_config.limit)
            logger.info(query)

            query_job = self.execute_query(
                project=project, query=query, job_config=self._job_config)
            if dry_run is False:
                saved_path = self.save_results(path=self._output, query_job=query_job)
                # pylint: disable=logging-not-lazy
                logger.info("Saved at %s" % saved_path)

    @staticmethod
    def save_results(
            path: str,
            query_job: bigquery.QueryJob,
            filename=AUDITLOG_FILE_NAME) -> str:
        """Save a query result to a file."""
        saved_dir = os.path.join(path, query_job.project)
        saved_path = os.path.join(saved_dir, filename)
        os.makedirs(saved_dir, exist_ok=True)
        # pylint: disable=unnecessary-comprehension
        with open(saved_path, "w") as fp:
            # results = [dict(row) for row in query_job.result()]
            for row in query_job.result():
                row_json = json.dumps(dict(row), default=serialize_json)
                fp.write(row_json + "\n")
        return saved_path

    @staticmethod
    def load_audit_logs(path: str) -> List[bigquery.Row]:
        """Load audit logs."""
        with open(path, "rb") as fp:
            return pickle.load(fp)

    @staticmethod
    def generate_query(
            project: str,
            dataset: str,
            start_date: str,
            end_date: str,
            limit: int = 100000) -> str:
        """Generate query"""
        # Get template file
        path = os.path.join(os.path.dirname(__file__), "template")
        template_loader = jinja2.FileSystemLoader(searchpath=path)
        template_env = jinja2.Environment(loader=template_loader, autoescape=True)
        template = template_env.get_template("get_insert_logs_v1.sql")

        # Render queries with the template.
        query = template.render(
            project=project,
            dataset=dataset,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )
        return query

    @staticmethod
    def execute_query(
            project: str,
            query: str,
            job_config: bigquery.QueryJobConfig = build_query_job_config()) -> bigquery.QueryJob:
        """Execute a BigQuery query"""
        client = bigquery.Client(project=project, default_query_job_config=job_config)
        query_job = client.query(query)
        return query_job
