#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys

from tools import get
from models import (
    Channel,
    Equipment,
    Station)


searched_site_code = 'CHMF'

# Configuration
server = 'localhost'
port = '8002'
if port:
    server = ':'.join([server, port])
api_url = 'http://%s/api/v1/' % server
site_url = api_url + 'sites/?format=json'
channel_url = api_url + 'channels/?format=json'
equipment_url = api_url + 'equipments/?format=json'


# Search Charmoille site
url = site_url + '&code=%s' % searched_site_code
stations = get(url)

# Then BROWSE data to fetch ALL NEEDED information
result = []
for station in stations:
    # Fetch its ID and some info
    s = Station(api_url, station)
    # Search linked channels
    url = channel_url + '&station=%s' % s.code
    channels = get(url)
    for channel in channels:
        # Fetch code, location code
        c = Channel(api_url, channel)
        c.station = s  # Add a link from channel to station
        s.channels.append(c)
        if c.network and c.network.code not in s.networks:
            s.networks.append(c.network.code)
    # Search equipments linked to the station, but not linked to a channel
    station_equipment_url = equipment_url + '&station=%s' % searched_site_code
    equipments = get(station_equipment_url)
    for equipment in equipments:
        e = Equipment(api_url, equipment)
        s.equipments.append(e)
    # Remember station
    result.append(s)

# FINALLY DISPLAY RESULT
for station in result:
    print(s)

# Bye bye!
sys.exit(0)
