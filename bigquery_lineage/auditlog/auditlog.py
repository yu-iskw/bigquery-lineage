# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
from __future__ import absolute_import, division, print_function

import json
from dataclasses import dataclass, field
from typing import Dict, Any, List


def read_auditlog(file: str):
    """Read a file of auditlog."""
    with open(file, "r") as fp:
        for line in fp:
            yield Auditlog.parse(json.loads(line))


@dataclass()
class BigQueryTableOrView:
    project: str = None
    dataset: str = None
    table: str = None

    def __str__(self):
        """Convert to str."""
        return '{}.{}.{}'.format(self.project, self.dataset, self.table)

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        block = {} if block is None else block
        return BigQueryTableOrView(
            project=block.get("projectId", None),
            dataset=block.get("datasetId", None),
            table=block.get("tableId", None),
        )

    def has_value(self):
        """Check if an instance has concrete values or not."""
        return (self.project is not None
                and self.dataset is not None
                and self.table is not None)


@dataclass()
class JobCompleteEvent:
    @dataclass()
    class JobConfiguration:
        @dataclass()
        class Load:
            # variables
            sourceUris: List[str] = None
            destinationTable: BigQueryTableOrView = None
            createDisposition: str = None
            writeDisposition: str = None

            @classmethod
            def parse(cls, block: Dict[str, Any]):
                return JobCompleteEvent.JobConfiguration.Load(
                    sourceUris=block.get("sourceUris", []),
                    destinationTable=BigQueryTableOrView.parse(block.get("destinationTable", {})),
                    createDisposition=block.get("createDisposition", None),
                    writeDisposition=block.get("writeDisposition", None),
                )

        @dataclass()
        class Query:
            # variables
            query: str = None
            destinationTable: BigQueryTableOrView = None
            createDisposition: str = None
            writeDisposition: str = None

            @classmethod
            def parse(cls, block: Dict[str, Any]):
                return JobCompleteEvent.JobConfiguration.Query(
                    query=block.get("query", None),
                    destinationTable=BigQueryTableOrView.parse(block.get("destinationTable", {})),
                    createDisposition=block.get("createDisposition", None),
                    writeDisposition=block.get("writeDisposition", None),
                )

        # variables
        load: Load = None
        query: Query = None

        @classmethod
        def parse(cls, block: Dict[str, Any]):
            load = block["load"] if "load" in block.keys() and block["load"] is not None else {}
            query = block["query"] if "query" in block.keys() and block["query"] is not None else {}
            return JobCompleteEvent.JobConfiguration(
                load=JobCompleteEvent.JobConfiguration.Load.parse(load),
                query=JobCompleteEvent.JobConfiguration.Query.parse(query),
            )

    @dataclass()
    class JobStatistics:
        # variables
        createTime: str = None
        startTime: str = None
        endTime: str = None
        referencedTables: List[BigQueryTableOrView] = None
        referencedViews: List[BigQueryTableOrView] = None

        @classmethod
        def parse(cls, block: Dict[str, Any]):
            return JobCompleteEvent.JobStatistics(
                createTime=block.get("createTime", None),
                startTime=block.get("startTime", None),
                endTime=block.get("endTime", None),
                referencedTables=[
                    BigQueryTableOrView(project=table["projectId"], dataset=table["datasetId"], table=table["tableId"])
                    for table in block.get("referencedTables", [])
                ],
                referencedViews=[
                    BigQueryTableOrView(project=view["projectId"], dataset=view["datasetId"], table=view["tableId"])
                    for view in block.get("referencedViews", [])
                ],
            )

    # variables
    eventName: str = None
    jobConfiguration: JobConfiguration = None
    jobStatistics: JobStatistics = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        job_configuration = block["job"].get("jobConfiguration", {}) if "job" in block.keys() else {}
        job_statistics = block["job"].get("jobStatistics", {}) if "job" in block.keys() else {}
        return JobCompleteEvent(
            eventName=block.get("eventName", None),
            jobConfiguration=JobCompleteEvent.JobConfiguration.parse(job_configuration),
            jobStatistics=JobCompleteEvent.JobStatistics.parse(job_statistics),
        )


@dataclass()
class AuthenticationInfo:
    principalEmail: str

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        return AuthenticationInfo(
            principalEmail=block["principalEmail"],
        )


@dataclass()
class ServicedataV1Bigquery:
    jobCompletedEvent: JobCompleteEvent = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        job_completed_event = (block["jobCompletedEvent"]
                               if "jobCompletedEvent" in block.keys()
                                  and block["jobCompletedEvent"] is not None
                               else {})
        return ServicedataV1Bigquery(
            jobCompletedEvent=JobCompleteEvent.parse(job_completed_event),
        )


@dataclass
class ProtopayloadAuditlog:
    methodName: str
    authenticationInfo: AuthenticationInfo
    servicedata_v1_bigquery: ServicedataV1Bigquery = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        servicedata_v1_bigquery = block.get("servicedata_v1_bigquery", {})
        return ProtopayloadAuditlog(
            methodName=block["methodName"],
            authenticationInfo=AuthenticationInfo.parse(block["authenticationInfo"]),
            servicedata_v1_bigquery=ServicedataV1Bigquery.parse(servicedata_v1_bigquery),
        )


@dataclass()
class Resource:
    project: str

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        return Resource(
            project=block["labels"]["project_id"],
        )


@dataclass
class Auditlog:
    resource: Resource = None
    protopayload_auditlog: ProtopayloadAuditlog = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        return Auditlog(
            resource=Resource.parse(block["resource"]),
            protopayload_auditlog=ProtopayloadAuditlog.parse(block["protopayload_auditlog"]),
        )
