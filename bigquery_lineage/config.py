# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class ConfigSource:
    project: str
    dataset: str
    table: str

    @classmethod
    def parse(cls, yaml: Dict[str, Any]):
        config_source = ConfigSource(
            project=yaml["project"],
            dataset=yaml["dataset"],
            table=yaml.get("table", "cloudaudit_googleapis_com_data_access_")
        )
        return config_source


@dataclass
class Config:
    start: str
    end: str
    limit: int = 1000000
    sources: List[ConfigSource] = None

    @classmethod
    def parse(cls, yaml: Dict[str, Any]):
        sources = [ConfigSource.parse(source) for source in yaml.get("sources", [])]
        config = Config(
            start=yaml["start"],
            end=yaml["end"],
            limit=yaml.get("limit", 100000),
            sources=sources,
        )
        return config
