#!/usr/bin/env bash
#
# Gives gissmo Docker IP
#

ip=`docker inspect gissmo1.8 | grep IPAddress | cut -d '"' -f 4`
#port=`docker inspect --format='{{(index (index .NetworkSettings.Ports "8000/tcp") 0).HostPort}}' gissmo`
port=8000
echo "$ip:$port"
