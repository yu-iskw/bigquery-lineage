#!/bin/bash
set -e

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Constants
DOCKER_TAG_BASE="yuiskw/bigquery-lineage"

# Arguments
mode=${1:?"mode is not set"}
docker_tag=${2:?"docker_tag is not set"}

# Validate arguments
if [[ "$mode" != "build" ]] && [[ "$mode" != "push" ]] ; then
  echo "model should be 'build' or 'push'."
  exit 1
fi

# Get the docker image name
docker_image="${DOCKER_TAG_BASE}:${docker_tag}"

# Build docker image
docker build --rm \
  -f "${PROJECT_DIR}"/docker/Dockerfile \
  -t "$docker_image" \
  "${PROJECT_DIR}"

# If mode is "push", then push the docker image.
if [[ "$mode" == "push" ]] ; then
  docker push "$docker_image"
fi
