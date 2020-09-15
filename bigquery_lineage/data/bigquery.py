# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
from typing import List
import json

import jinja2
from google.cloud import bigquery


def build_query_job_config(**kwargs) -> bigquery.QueryJobConfig:
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
                 projects: List[str],
                 start_date: str,
                 end_date: str,
                 job_config: bigquery.QueryJobConfig = build_query_job_config()):
        self._projects = projects
        self._start_date = start_date
        self._end_date = end_date
        self._query_job_config = job_config

    def export_logs(self, base_path: str) -> None:
        """Export BigQuery audit logs to files respectively
        The outputs are files. Each file contains audit logs in a GCP project.

        :param base_path: Path to the base directory to store exported logs.
        """
        # Make the base directory.
        os.makedirs(base_path, exist_ok=True)
        # Export logs of project respectively
        for project in self._projects:
            # Get a query.
            query = BigQueryDataCollector.generate_query(
                project, self._start_date, self._end_date)
            # Export logs to a file.
            with open(os.path.join(base_path, project), "w") as fp:
                query_job = self.__class__.execute_query(
                    project=project,
                    query=query,
                    job_config=self._query_job_config)
                for row in query_job:
                    line = json.dumps(dict(row))
                    fp.write(line)

    def generate_queries(self) -> List[str]:
        """Generate BigQuery queries to get insert jobs.

        NOTE: The reason why we separate queries is locations of BigQuery tables
              of audit logs are potentially different. In that case, it is impossible
              to join tables.
        """
        # Render queries with the template.
        queries = [BigQueryDataCollector.generate_query(
            project=project,
            start_date=self._start_date,
            end_date=self._end_date
        ) for project in self._projects]
        return queries

    @staticmethod
    def generate_query(
            project: str,
            start_date: str,
            end_date: str) -> str:
        """Generate query"""
        # Get template file
        path = os.path.join(os.path.dirname(__file__), "template")
        template_loader = jinja2.FileSystemLoader(searchpath=path)
        template_env = jinja2.Environment(loader=template_loader, autoescape=True)
        template = template_env.get_template("get_insert_logs_v1.sql")

        # Render queries with the template.
        query = template.render(
            project=project,
            start_date=start_date,
            end_date=end_date
        )
        return query

    @staticmethod
    def execute_query(
            project: str,
            query: str,
            job_config: bigquery.QueryJobConfig = None) -> bigquery.QueryJob:
        """Execute a BigQuery query"""
        client = bigquery.Client(project=project, default_query_job_config=job_config)
        query_job = client.query(query)
        return query_job
