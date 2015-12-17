#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import sys

searched_site_code = 'CHARMOILLE'

# Configuration
server = 'localhost'
port = '8000'
if port:
    server = ':'.join([server, port])
api_url = 'http://%s/api/' % server
site_url = api_url + 'sites/?format=json'
channel_url = api_url + 'channels/?format=json'
equipment_url = api_url + 'equipments/?format=json'


class Station(object):
    def __init__(self, data_dict):
        fields = [
            'id',
            'code',
            'latitude',
            'longitude',
            'elevation',
            'name',
            'region',
            'county',
            'country',
            'town',
        ]
        for field in fields:
            setattr(self, field, data_dict.get(field, None))
        self.channels = []

    def get_channels(self):
        res = ''
        for channel in self.channels:
            res += '\n%s' % str(channel)
        return res

    def __str__(self):
        result = """STATION %s%s"""
        return result % (self.code, self.get_channels())


class Channel(object):
    def __init__(self, data_dict):
        fields = [
            'id',
            'code',
            'location_code',
            'start_date',
            'equipments',
        ]
        for field in fields:
            setattr(self, field, data_dict.get(field, None))
        # Fetch equipments
        self.equipment_links = self.equipments
        self.equipments = []
        for link in self.equipment_links:
            data = get(link)
            self.equipments.append(Equipment(data))

    def get_equipments(self):
        res = ''
        for equipment in self.equipments:
            res += '\n%s' % str(equipment)
        return res

    def __str__(self):
        result = """» Channel %s%s"""
        return result % (self.code, self.get_equipments())


class Equipment(object):
    def __init__(self, data_dict):
        fields = [
            'id',
            'name',
            'type',
            'serial_number',
            'vendor',
            'station',
        ]
        for field in fields:
            setattr(self, field, data_dict.get(field, None))

    def __str__(self):
        result = """|  → EQUIPMENT (%s): %s"""
        return result % (self.type, self.name)


def get(url):
    data = []
    request = requests.get(url)
    if request:
        data = request.json()
    return data

# Search Charmoille site
url = site_url + '&name=%s' % searched_site_code
stations = get(url)
for station in stations:
    # Fetch its ID and some info
    s = Station(station)
    # Search linked channels
    url = channel_url + '&station=%s' % s.code
    channels = get(url)
    for channel in channels:
        # Fetch code, location code
        c = Channel(channel)
        s.channels.append(c)
    # Display result
    print(s)

sys.exit(0)
