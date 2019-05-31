#!/usr/bin/env bash

set -e

PARAMS=""
BIND_DIRECTORY="$(pwd)"

while (( "$#" )); do
  case "$1" in
    -b|--bind-directory)
      BIND_DIRECTORY=$2
      shift 2
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

eval set -- "$PARAMS"

# Note BIND_DIRECTORY in this context translates to the bind mount
# created in the container. It DOES not carry over to -d argument of
# the artifacts script. For instance, if this script is invoked with
# `exhibitor-tls-artifacts -d /tmp 10.0.0.1 10.0.0.2`, then the
# resulting output directory would be `/tmp/artifacts`

docker run --rm -v ${BIND_DIRECTORY}:/build --workdir=/build {{DOCKER_IMAGE}} ${PARAMS}
