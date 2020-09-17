# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import Dict, Any, List

import re

from bigquery_lineage.utils import load_yaml


@dataclass
class ConfigSource:
    project: str
    dataset: str

    @classmethod
    def parse(cls, yaml: Dict[str, Any]):
        """Parse dict derives from YAML."""
        config_source = ConfigSource(
            project=yaml["project"],
            dataset=yaml["dataset"],
        )
        return config_source


@dataclass
class ConfigFilters:
    @dataclass
    class ExcludedTable:
        project_regexp: str = None
        dataset_regexp: str = None
        table_regexp: str = None

        @classmethod
        def parse(cls, block: Dict[str, Any]):
            return ConfigFilters.ExcludedTable(
                project_regexp=block.get("project_regexp", None),
                dataset_regexp=block.get("dataset_regexp", None),
                table_regexp=block.get("table_regexp", None))

        def match(self, project: str, dataset: str, table: str):
            """Check if a table matches with regexp or not."""
            couples = [
                (self.project_regexp, project),
                (self.dataset_regexp, dataset),
                (self.table_regexp, table)]
            for regexp, target in couples:
                # Skip if regexp is None
                if regexp is None:
                    continue
                compiled_regexp = re.compile(r'{}'.format(regexp))
                if compiled_regexp.search(target):
                    return True
            return False

    # variables
    excluded_tables: List[ExcludedTable] = None
    excluded_principal_emails: List[str] = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        excluded_tables = block.get("excluded_tables", [])
        return ConfigFilters(
            excluded_tables=[ConfigFilters.ExcludedTable.parse(b) for b in excluded_tables],
            excluded_principal_emails=block.get("excluded_principal_emails", [])
        )

    def is_excluded_table(self, project: str, dataset: str, table: str):
        """Check if a given email is matched with any of excluded table."""
        return any([x.match(project=project, dataset=dataset, table=table)
                    for x in self.excluded_tables])

    def is_excluded_principal_email(self, email: str):
        """Check if a given email is matched with any of excluded principal emails."""
        regexps = [re.compile(r'{}'.format(e)) for e in self.excluded_principal_emails]
        return any([regexp.search(email) for regexp in regexps])


@dataclass
class Config:
    start: str
    end: str
    limit: int = 1000000
    sources: List[ConfigSource] = None
    filters: ConfigFilters = None

    @classmethod
    def parse(cls, yaml: Dict[str, Any]):
        """Parse dict derives from YAML."""
        sources = [ConfigSource.parse(source) for source in yaml.get("sources", [])]
        config = Config(
            start=yaml["start"],
            end=yaml["end"],
            limit=yaml.get("limit", 100000),
            sources=sources,
            filters=ConfigFilters.parse(yaml.get("filters", {})),
        )
        return config

    @classmethod
    def load(cls, path):
        """Load a config from a file."""
        yaml_block = load_yaml(path)
        bql_config = Config.parse(yaml=yaml_block)
        return bql_config
