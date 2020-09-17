# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import List, Tuple

import pydot

from bigquery_lineage.auditlog.auditlog import Auditlog


COLOR_GCP = "pastel25/5"
COLOR_BQ = "pastel25/4"
COLOR_BQ_PROJECT = "pastel25/3"
COLOR_BQ_DATASET = "pastel25/2"
COLOR_BQ_TABLE = "pastel25/1"


def create_bigquery_project_cluster(project: str) -> pydot.Cluster:
    """Create a cluster of a BigQuery project."""
    name = "cluster_bq_project_{}".format(project)
    label = project
    return pydot.Cluster(graph_name=name, label=label, color=COLOR_BQ_PROJECT, style="filled")


def create_dataset_project_cluster(project: str, dataset: str) -> pydot.Cluster:
    """Create a cluster of a BigQuery dataset."""
    name = "cluster_bq_dataset_{}_{}".format(project, dataset)
    label = "{}.{}".format(project, dataset)
    dataset_cluster = pydot.Cluster(graph_name=name, label=label, color=COLOR_BQ_DATASET, style="filled")
    return dataset_cluster


def create_bigquery_table_node(project: str, dataset: str, table: str) -> pydot.Node:
    """Create a node of BigQuery table."""
    table_id = get_bigquery_full_table_id(project=project, dataset=dataset, table=table)
    return pydot.Node(name=table_id, label=table_id, shape="box", color=COLOR_BQ_TABLE, style="filled")


def get_bigquery_full_table_id(project: str, dataset: str, table: str) -> str:
    """Get a BigQuery full table ID."""
    return '{}.{}.{}'.format(project, dataset, table)


@dataclass()
class PydotBuilderV1:
    bigquery_references: List[Tuple[Tuple[str, str, str], Tuple[str, str, str]]] = None

    def update(self, auditlog: Auditlog):
        """Update reference relationships."""
        self.update_with_job_completed_event_query(auditlog=auditlog)

    def update_with_job_completed_event_query(self, auditlog: Auditlog):
        """Update reference relationships with JobCompletedEvent.query."""
        job_statistics = (auditlog.protopayload_auditlog.servicedata_v1_bigquery
                          .jobCompletedEvent.jobStatistics)
        query = (auditlog.protopayload_auditlog.servicedata_v1_bigquery
                 .jobCompletedEvent.jobConfiguration.query)

        # Check if a destination table exists.
        if not query.destinationTable.has_value():
            return None

        # Initialize the array just in case, if necessary.
        if self.bigquery_references is None:
            self.bigquery_references = []

        # Destination node
        destination_node_key = (
            query.destinationTable.project,
            query.destinationTable.dataset,
            query.destinationTable.table)
        # Loop over referenced tables.
        if (job_statistics.referencedTables is not None
                and len(job_statistics.referencedTables) > 0):
            # Source nodes
            source_node_keys = [
                (referenced_table.project, referenced_table.dataset, referenced_table.table)
                for referenced_table in job_statistics.referencedTables
                if referenced_table.has_value()
            ]
            for source_node_key in source_node_keys:
                self.bigquery_references.append((source_node_key, destination_node_key))
        # Loop over referenced views.
        if (job_statistics.referencedViews is not None
                and len(job_statistics.referencedViews) > 0):
            # Source nodes
            source_node_keys = [
                (referenced_view.project, referenced_view.dataset, referenced_view.table)
                for referenced_view in job_statistics.referencedTables
                if referenced_view.has_value()
            ]
            for source_node_key in source_node_keys:
                self.bigquery_references.append((source_node_key, destination_node_key))

    def build(self) -> pydot.Dot:
        """Build a graph."""
        graph = pydot.Dot(
            graph_name="Google Cloud Platform",
            graph_type="digraph",
            color=COLOR_GCP,
            style="filled",
            rankdir="LR")
        subgraph_bq = pydot.Cluster(
            graph_name="cluster_BigQuery",
            graph_type="digraph",
            color=COLOR_BQ,
            style="filled",
            label="BigQuery")

        subgraph_bq_projects = {}
        table_nodes = {}
        # Create nodes and edges
        for bq_reference in self.bigquery_references:
            ((src_project, src_dataset, src_table),
             (dst_project, dst_dataset, dst_table)) = bq_reference
            # Initialize a BigQuery project for source.
            if src_project not in subgraph_bq_projects:
                subgraph_bq_projects[src_project] = {
                    'subgraph': create_bigquery_project_cluster(project=src_project),
                    'datasets': {},
                }
            # Initialize a BigQuery dataset for source.
            if src_dataset not in subgraph_bq_projects[src_project]["datasets"]:
                subgraph_bq_projects[src_project]["datasets"][src_dataset] = create_dataset_project_cluster(
                    project=src_project, dataset=src_dataset)
            # Initialize a BigQuery project for destination
            if dst_project not in subgraph_bq_projects:
                subgraph_bq_projects[dst_project] = {
                    'subgraph': create_bigquery_project_cluster(project=dst_project),
                    'datasets': {},
                }
            # Initialize a BigQuery dataset for destination.
            if dst_dataset not in subgraph_bq_projects[dst_project]["datasets"]:
                subgraph_bq_projects[dst_project]["datasets"][dst_dataset] = create_dataset_project_cluster(
                    project=dst_project, dataset=dst_dataset)

            # Create source and destination nodes.
            source_node_id = get_bigquery_full_table_id(
                project=src_project, dataset=src_dataset, table=src_table)
            source_id = table_nodes.get(
                source_node_id,
                create_bigquery_table_node(project=src_project, dataset=src_dataset, table=src_table))
            destination_node_id = get_bigquery_full_table_id(
                project=dst_project, dataset=dst_dataset, table=dst_table)
            destination_node = table_nodes.get(
                destination_node_id,
                create_bigquery_table_node(project=dst_project, dataset=dst_dataset, table=dst_table))
            # Register the nodes.
            subgraph_bq_projects[src_project]["datasets"][src_dataset].add_node(source_id)
            subgraph_bq_projects[dst_project]["datasets"][dst_dataset].add_node(destination_node)
            # Create an edge.
            edge = pydot.Edge(source_id, destination_node)
            # Register the edge.
            if src_project == dst_project and src_dataset == dst_dataset:
                subgraph_bq_projects[src_project]["datasets"][src_dataset].add_edge(edge)
            elif src_project == dst_project:
                subgraph_bq_projects[src_project]["subgraph"].add_edge(edge)
            else:
                subgraph_bq.add_edge(edge)

        # Link subgraphs
        for project in subgraph_bq_projects.keys():
            subgraph_project = subgraph_bq_projects[project]["subgraph"]
            for dataset in subgraph_bq_projects[project]["datasets"].keys():
                subgraph_dataset = subgraph_bq_projects[project]["datasets"][dataset]
                subgraph_project.add_subgraph(subgraph_dataset)
            subgraph_bq.add_subgraph(subgraph_project)
        graph.add_subgraph(subgraph_bq)
        return graph