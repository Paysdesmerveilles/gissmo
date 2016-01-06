# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tools import get


# Default values
default_degree_unit = '°'
default_sample_unit = 'Hz'
default_elevation_unit = 'm'

# Some data
api_service_name = 'services'
api_ip_name = 'ipaddresses'


class APIObject(object):
    def __init__(self, api_url, fields, data_dict):
        for field in fields:
            setattr(self, field, data_dict.get(field, ''))
        self.api_url = api_url


class Actor(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'name',
        ]
        super(Actor, self).__init__(api_url, fields, data_dict)

    def __str__(self):
        return '%s' % self.name


class Station(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'id',
            'code',
            'latitude',
            'latitude_unit',
            'longitude',
            'longitude_unit',
            'elevation',
            'elevation_unit',
            'azimuth',
            'azimuth_unit',
            'name',
            'region',
            'county',
            'country',
            'town',
            'geology',
            'operator',
        ]
        super(Station, self).__init__(api_url, fields, data_dict)
        self.channels = []
        self.networks = []
        # Fetch operator if needed
        self.operator_link = self.operator
        self.operator = ''
        if self.operator_link:
            data = get(self.operator_link)
            if data:
                self.operator = Actor(api_url, data)
        # Fix unit for longitude, latitude
        for field in ['latitude', 'longitude', 'azimuth']:
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
    def __init__(self, api_url, data_dict):
        fields = [
            'code',
        ]
        super(Network, self).__init__(api_url, fields, data_dict)

    def __str__(self):
        return '%s' % self.code


class Address(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'ip',
            'netmask',
        ]
        super(Address, self).__init__(api_url, fields, data_dict)

    def __str__(self):
        return '%s/%s' % (self.ip, self.netmask)


class Service(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'protocol',
            'port',
        ]
        super(Service, self).__init__(api_url, fields, data_dict)

    def __str__(self):
        return '%s' % self.protocol


class Channel(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'id',
            'code',
            'location_code',
            'start_date',
            'sample_rate',
            'sample_rate_unit',
            'chains',
            'equipments',
            'network',
        ]
        super(Channel, self).__init__(api_url, fields, data_dict)
        self.station = None
        # Equipment preparation
        self.equipment_links = self.equipments
        self.equipments = []
        # Fetch equipment regarding chains
        for chain_link in self.chains:
            c_data = get(chain_link)
            c = Chain(api_url, c_data)
            if c.equipment:
                e_data = get(c.equipment)
                e = Equipment(api_url, e_data)
                e.chain_order = c.type
                e.channel = self
                self.equipments.append(e)
        # Fetch network
        self.network_link = self.network
        if self.network_link:
            n_data = get(self.network_link)
            if n_data:
                self.network = Network(api_url, n_data)
        # Fix missing rate unit
        if not self.sample_rate_unit:
            self.sample_rate_unit = default_sample_unit

    def get_equipments(self):
        res = ''
        for equipment in self.equipments:
            res += '\n%s' % str(equipment)
        return res

    def __str__(self):
        result = """» Channel %s [rate: %s%s, location: %s] (%s)%s"""
        name = '_'.join([
            self.network.code,
            self.station.code,
            self.code,
            self.location_code])
        return result % (
            self.code,
            self.sample_rate,
            self.sample_rate_unit,
            self.location_code,
            name,
            self.get_equipments())


class Equipment(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'id',
            'name',
            'type',
            'serial_number',
            'vendor',
            'station',
        ]
        super(Equipment, self).__init__(api_url, fields, data_dict)
        # Specific process
        if not self.vendor:
            self.vendor = ''
        # Additionnal field
        self.chain_order = 'Unknown'
        self.channel = None
        # Network configuration
        self.addresses = self._fetch_addresses(self.id)
        self.services = self._fetch_services(self.id)

    def _fetch_addresses(self, object_id):
        """
        Get addresses from the given equipment.
        """
        res = []
        ip_url = '%s%s/?format=json' % (self.api_url, api_ip_name)
        data = get('%s&equipment=%s' % (ip_url, object_id))
        if data:
            for element in data:
                address = Address(self.api_url, element)
                res.append(address)
        return res

    def _fetch_services(self, object_id):
        """
        Get service from the given equipment.
        """
        res = []
        service_url = '%s%s/?format=json' % (self.api_url, api_service_name)
        data = get('%s&equipment=%s' % (service_url, object_id))
        if data:
            for element in data:
                service = Service(self.api_url, element)
                res.append(service)
        return res

    def get_addresses(self):
        res = ''
        for address in self.addresses:
            res += '\n|        ⋅ %s' % str(address)
        return res

    def get_services(self):
        res = ''
        for service in self.services:
            res += '\n|        ⋅ %s: %s' % (service.port, service.protocol)
        return res

    def __str__(self):
        result = """|  → EQUIPMENT (%s)
|      Vendor: %s
|      Model:  %s
|      S/N:    %s"""
        data = [
            self.chain_order,
            self.vendor,
            self.name,
            self.serial_number]
        if self.chain_order == 'Sensor':
            result += """
|      Azimuth: %s%s"""
            azimuth = self.channel.station.azimuth
            if azimuth:
                data += [azimuth, self.channel.station.azimuth_unit]
            else:
                data += ['', '']
        # Add Network configuration
        if self.addresses:
            result += """
|      IP/Netmask: %s"""
            data += [self.get_addresses()]
        if self.services:
            result += """
|      Services: %s"""
            data += [self.get_services()]
        return result % tuple(data)


class Chain(APIObject):
    def __init__(self, api_url, data_dict):
        fields = [
            'id',
            'type',
            'channel',
            'equipment',
        ]
        super(Chain, self).__init__(api_url, fields, data_dict)

    def __str__(self):
        return '%s' % self.type
