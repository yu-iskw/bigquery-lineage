#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

pylint -v "${PROJECT_DIR}"/bigquery_lineage "${PROJECT_DIR}"/tests
