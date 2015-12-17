#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests
import sys

searched_site_code = 'CHMF'
default_degree_unit = '°'
default_sample_unit = 'Hz'
default_elevation_unit = 'm'

# Configuration
server = 'localhost'
port = '8000'
if port:
    server = ':'.join([server, port])
api_url = 'http://%s/api/' % server
site_url = api_url + 'sites/?format=json'
channel_url = api_url + 'channels/?format=json'
equipment_url = api_url + 'equipments/?format=json'


class APIObject(object):
    def __init__(self, fields, data_dict):
        for field in fields:
            setattr(self, field, data_dict.get(field, None))


class Actor(APIObject):
    def __init__(self, data_dict):
        fields = [
            'name',
        ]
        super(Actor, self).__init__(fields, data_dict)

    def __str__(self):
        return '%s' % self.name


class Station(APIObject):
    def __init__(self, data_dict):
        fields = [
            'id',
            'code',
            'latitude',
            'latitude_unit',
            'longitude',
            'longitude_unit',
            'elevation',
            'elevation_unit',
            'name',
            'region',
            'county',
            'country',
            'town',
            'geology',
            'operator',
        ]
        super(Station, self).__init__(fields, data_dict)
        self.channels = []
        self.networks = []
        # Fetch operator if needed
        self.operator_link = self.operator
        self.operator = None
        if self.operator_link:
            data = get(self.operator_link)
            if data:
                self.operator = Actor(data)
        # Fix unit for longitude, latitude
        for field in ['latitude', 'longitude']:
            field_unit = '_'.join([field, 'unit'])
            if not getattr(self, field_unit, None):
                setattr(self, field_unit, default_degree_unit)
        # Then elevation
        if not self.elevation_unit:
            self.elevation_unit = default_elevation_unit
        # Geology
        if not self.geology:
            self.geology = 'Unknown'

    def get_channels(self):
        res = ''
        for channel in self.channels:
            res += '\n%s' % str(channel)
        return res

    def __str__(self):
        result = """STATION: %s
  Name: %s
  Operator: %s
  Networks: %s
  Latitude: %s%s
  Longitude: %s%s
  Elevation: %s%s
  Geology: %s
  %s"""
        return result % (
            self.code,
            self.name,
            self.operator,
            self.networks,
            self.latitude,
            self.latitude_unit,
            self.longitude,
            self.longitude_unit,
            self.elevation,
            self.elevation_unit,
            self.geology,
            self.get_channels())


class Network(APIObject):
    def __init__(self, data_dict):
        fields = [
            'code',
        ]
        super(Network, self).__init__(fields, data_dict)

    def __str__(self):
        return '%s' % self.code


class Channel(APIObject):
    def __init__(self, data_dict):
        fields = [
            'id',
            'code',
            'location_code',
            'start_date',
            'sample_rate',
            'sample_rate_unit',
            'equipments',
            'network',
        ]
        super(Channel, self).__init__(fields, data_dict)
        # Fetch equipments
        self.equipment_links = self.equipments
        self.equipments = []
        for link in self.equipment_links:
            e_data = get(link)
            if e_data:
                self.equipments.append(Equipment(e_data))
        # Fetch network
        self.network_link = self.network
        if self.network_link:
            n_data = get(self.network_link)
            if n_data:
                self.network = Network(n_data)
        # Fix missing rate unit
        if not self.sample_rate_unit:
            self.sample_rate_unit = default_sample_unit

    def get_equipments(self):
        res = ''
        for equipment in self.equipments:
            res += '\n%s' % str(equipment)
        return res

    def __str__(self):
        result = """» Channel %s [rate: %s%s]%s"""
        return result % (
            self.code,
            self.sample_rate,
            self.sample_rate_unit,
            self.get_equipments())


class Equipment(APIObject):
    def __init__(self, data_dict):
        fields = [
            'id',
            'name',
            'type',
            'serial_number',
            'vendor',
            'station',
        ]
        super(Equipment, self).__init__(fields, data_dict)

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
url = site_url + '&code=%s' % searched_site_code
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
        if c.network and c.network.code not in s.networks:
            s.networks.append(c.network.code)
    # Display result
    print(s)

sys.exit(0)
