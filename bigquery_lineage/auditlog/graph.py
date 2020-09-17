# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import urlsplit


@dataclass()
class BigQueryTable:
    project: str = None
    dataset: str = None
    table: str = None

    def __str__(self):
        return '{}.{}.{}'.format(self.project, self.dataset, self.table)

    def __eq__(self, other):
        if (self.project == other.project
                and self.dataset == other.dataset
                and self.table == other.table):
            return True
        return False


@dataclass()
class BigQueryDataset:
    project: str = None
    dataset: str = None
    tables: List[str] = None

    def add(self, project: str, dataset: str, table: str):
        if project != self.project or dataset != self.dataset:
            raise ValueError("invalid dataset: {} != {}".format(self.dataset, dataset))
        table = BigQueryTable(project=project, dataset=dataset, table=table)
        if not any([table == t for t in self.tables]):
            self.tables.append(table)


@dataclass()
class BigQueryProject:
    project: str
    datasets: List[BigQueryDataset] = None

    def add(self, project: str, dataset: str):
        if project != self.project or dataset != self.dataset:
            raise ValueError("invalid dataset: {} != {}".format(self.dataset, dataset))


@dataclass()
class GoogleCloudStorageObject:
    path: str
    bucket: str


@dataclass()
class GoogleCloudStorageBucket:
    bucket: str
    project: str = None
    objects: List[GoogleCloudStorageObject] = None

    def __init__(self):
        self.objects = []

    def __eq__(self, other):
        if self.bucket == other.bucket:
            return True
        return False


@dataclass()
class GoogleCloudStorage:
    project: str = None
    buckets: List[GoogleCloudStorageBucket] = None

    def __init__(self):
        self.buckets = []

    def add_bucket(self, bucket):
        bucket = GoogleCloudStorageBucket(bucket=bucket)
        if not any([bucket == b for b in self.buckets]):
            self.buckets.append(bucket)

    @classmethod
    def get_bucket(self, uri):
        (scheme, netloc, path, query, fragment) = urlsplit(uri)
        bucket_name = netloc
        return bucket_name


@dataclass()
class GoogleCloudProject:
    project: str
    bigquery: List[BigQueryProject]
    gcs: List[GoogleCloudStorage]

    def __init__(self):
        self.bigquery = []
        self.gcs = []


@dataclass()
class GoogleCloud:
    projects: List[GoogleCloudProject]