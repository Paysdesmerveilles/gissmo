#!/usr/bin/env bash
#
# Launch gissmo Docker instance
#

docker run --rm -it -p :8000 -v `pwd`:/opt/gissmo --name=gissmo gissmo:latest
