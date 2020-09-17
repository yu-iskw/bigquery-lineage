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
    # variables
    excluded_tables: List[str] = None
    excluded_principal_emails: List[str] = None

    @classmethod
    def parse(cls, block: Dict[str, Any]):
        return ConfigFilters(
            excluded_tables=block.get("excluded_tables", []),
            excluded_principal_emails=block.get("excluded_principal_emails", [])
        )

    def is_excluded_principal_email(self, email: str):
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
