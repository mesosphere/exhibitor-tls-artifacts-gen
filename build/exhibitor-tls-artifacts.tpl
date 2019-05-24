#!/usr/bin/env bash

set -e

PARAMS=""
OUTPUT_DIRECTORY="$(pwd)"

while (( "$#" )); do
  case "$1" in
    -d|--directory)
      OUTPUT_DIRECTORY=$2
      shift 2
      ;;
    --) # end argument parsing
      shift
      break
      ;;
    -*|--*=) # unsupported flags
      echo "Error: Unsupported flag $1" >&2
      exit 1
      ;;
    *) # preserve positional arguments
      PARAMS="$PARAMS $1"
      shift
      ;;
  esac
done

eval set -- "$PARAMS"

docker run -it --rm -v ${OUTPUT_DIRECTORY}:/build --workdir=/build {{DOCKER_IMAGE}} ${PARAMS}
