# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from pprint import pprint
from typing import Dict, Any, List


@dataclass()
class BigQueryTable:
    project: str = None
    dataset: str = None
    table: str = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        return BigQueryTable(
            project=block.get("projectId", None),
            dataset=block.get("datasetId", None),
            table=block.get("tableId", None),
        )


@dataclass()
class JobCompleteEvent:

    @dataclass()
    class JobConfiguration:
        @dataclass()
        class Load:
            # variables
            sourceUris: List[str] = None
            destinationTable: BigQueryTable = None
            createDisposition: str = None
            writeDisposition: str = None

            @classmethod
            def parse(cls, block: Dict[str, Any]):
                destinationTable = BigQueryTable(
                    project=block.get("destinationTable")
                )
                return JobCompleteEvent.JobConfiguration.Load(
                    sourceUris=block.get("sourceUris", []),
                    destinationTable=BigQueryTable.parse(block.get("destinationTable", {})),
                    createDisposition=block.get("createDisposition", None),
                    writeDisposition=block.get("writeDisposition", None),
                )

        @dataclass()
        class Query:
            # variables
            query: str = None
            destinationTable: BigQueryTable = None
            createDisposition: str = None
            writeDisposition: str = None

            @classmethod
            def parse(cls, block: Dict[str, Any]):
                return JobCompleteEvent.JobConfiguration.Query(
                    query=block.get("query", None),
                    destinationTable=BigQueryTable.parse(block.get("destinationTable", {})),
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
        referencedTables: List[BigQueryTable] = None

        @classmethod
        def parse(cls, block: Dict[str, Any]):
            return JobCompleteEvent.JobStatistics(
                createTime=block.get("createTime", None),
                startTime=block.get("startTime", None),
                endTime=block.get("endTime", None),
                referencedTables=[
                    BigQueryTable(project=table["projectId"], dataset=table["datasetId"], table=table["tableId"])
                    for table in block.get("referencedTables", [])
                ]
            )

    # variables
    jobConfiguration: JobConfiguration = None
    jobStatistics: JobStatistics = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        job_configuration = block["job"].get("jobConfiguration", JobCompleteEvent.JobConfiguration())
        job_statistics = block["job"].get("jobStatistics", JobCompleteEvent.JobStatistics())
        return JobCompleteEvent(
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
        job_completed_event = block.get("jobCompletedEvent", JobCompleteEvent())
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
        return ProtopayloadAuditlog(
            methodName=block["methodName"],
            authenticationInfo=AuthenticationInfo.parse(block["authenticationInfo"]),
            servicedata_v1_bigquery=ServicedataV1Bigquery.parse(
                block.get("servicedata_v1_bigquery", ServicedataV1Bigquery()))
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