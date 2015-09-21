#!/usr/bin/env bash
#
# Launch GISSMO application in Firefox from gissmo Docker instance
#

address=`./scripts/docker_ip.sh`
firefox http://$address/gissmo/ &
