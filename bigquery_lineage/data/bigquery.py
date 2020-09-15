# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import os
import logging
import pickle
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
                 output: str,
                 projects: List[str],
                 start_date: str,
                 end_date: str,
                 limit: int,
                 job_config: bigquery.QueryJobConfig = build_query_job_config()):
        self._output = output
        self._projects = projects
        self._start_date = start_date
        self._end_date = end_date
        self._limit = limit
        self._job_config = job_config

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
                project=project,
                start_date=self._start_date,
                end_date=self._end_date,
                limit=self._limit)
            # Export logs to a file.
            with open(os.path.join(base_path, project), "w") as fp:
                query_job = self.__class__.execute_query(
                    project=project,
                    query=query,
                    job_config=self._job_config)
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

    def run(self, dry_run: bool) -> None:
        for project in self._projects:
            query = self.generate_query(
                project=project, start_date=self._start_date,
                end_date=self._end_date, limit=self._limit)
            query_job = self.execute_query(
                project=project, query=query, job_config=self._job_config)
            logging.info(query_job.query_plan)
            if dry_run is False:
                query_job = self.execute_query(
                    project=project, query=query, job_config=self._job_config)
                self.save_results(path=self._output, query_job=query_job)

    @staticmethod
    def save_results(
            path: str,
            query_job: bigquery.QueryJob,
            filename="auditlog.pickle") -> str:
        """Save a query result to a file."""
        saved_dir = os.path.join(path, query_job.project)
        saved_path = os.path.join(saved_dir, filename)
        os.makedirs(saved_dir, exist_ok=True)
        results = [row for row in query_job.result()]
        with open(saved_path, "wb") as fp:
            pickle.dump(results, fp)
        return saved_path

    @staticmethod
    def load_results(path: str) -> List[bigquery.Row]:
        with open(path, "rb") as fp:
            return pickle.load(fp)

    @staticmethod
    def generate_query(
            project: str,
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