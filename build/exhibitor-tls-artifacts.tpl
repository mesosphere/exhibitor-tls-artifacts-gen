#!/usr/bin/env bash

# set -ex

docker run -it --rm -v $(pwd):/build --workdir /build {{DOCKER_IMAGE}} $@