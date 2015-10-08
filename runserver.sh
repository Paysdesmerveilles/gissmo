#!/usr/bin/env bash
#
# Launch Django server for gissmo Docker instance
#

docker-compose run --rm --service-ports web
