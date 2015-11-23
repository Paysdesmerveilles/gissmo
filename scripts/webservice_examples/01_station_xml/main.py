#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import sys

# Configuration
server = 'localhost:8002'
username = 'olivier'
password = 'olivier'
apiurl = 'http://%s/api/' % server
api_sites = '%ssites/' % apiurl
api_channels = '%schannels/' % apiurl


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
            res += '  %s\n' % str(channel)
        return res

    def __str__(self):
        result = """<Station code="%s">
  %s</Station>"""
        return result % (self.code, self.get_channels())


class Channel(object):
    def __init__(self, data_dict):
        fields = [
            'id',
            'code',
            'location_code',
            'start_date',
        ]
        for field in fields:
            setattr(self, field, data_dict.get(field, None))

    def __str__(self):
        result = """<Channel code="%s" locationCode="%s" startDate="%s">
  </Channel>"""
        return result % (self.code, self.location_code, self.start_date)


def get(url):
    data = []
    request = requests.get(url, auth=(username, password))
    if request:
        data = request.json()
    return data

# Search Charmoille site
url = api_sites + '?name=CHARMOILLE'
stations = get(url)
for station in stations:
    # Fetch its ID and some info
    s = Station(station)
    # Search linked channels
    url = api_channels + '?station=%s' % s.code
    channels = get(url)
    for channel in channels:
        # Fetch code, location code
        c = Channel(channel)
        s.channels.append(c)
    print(s)
# Get all channels info

sys.exit(0)
