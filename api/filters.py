# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from gissmo.models import (
    Actor,
    CalibrationUnit,
    Chain,
    Channel,
    DataType,
    Equipment,
    IPAddress,
    Network,
    Service,
    StationSite,
)

import django_filters


class ActorFilter(django_filters.FilterSet):
    """
    Enables filtering on Actor.
    """
    name = django_filters.CharFilter(name='actor_name')
    type = django_filters.ChoiceFilter(
        name='actor_type',
        choices=Actor.ACTOR_TYPE_CHOICES)

    class Meta:
        model = Actor
        fields = [
            'name',
            'type',
        ]


class SiteFilter(django_filters.FilterSet):
    """
    Enables filtering on Site.
    """
    name = django_filters.CharFilter(name="site_name")
    code = django_filters.CharFilter(name="station_code")
    type = django_filters.ChoiceFilter(
        name="site_type",
        choices=StationSite.SITE_CHOICES)
    restricted_status = django_filters.ChoiceFilter(
        choices=StationSite.STATUS)

    class Meta:
        model = StationSite
        fields = [
            'name',
            'code',
            'alternate_code',
            'historical_code',
            'latitude_unit',
            'longitude_unit',
            'elevation_unit',
            'type',
            'town',
            'region',
            'country',
        ]


class NetworkFilter(django_filters.FilterSet):
    """
    Enables filtering on Network.
    """
    name = django_filters.CharFilter(name='network_name')
    code = django_filters.CharFilter(name='network_code')
    restricted_status = django_filters.ChoiceFilter(
        choices=Network.STATUS)
    min_start_date = django_filters.DateTimeFilter(
        name='start_date',
        lookup_type='gte')
    max_start_date = django_filters.DateTimeFilter(
        name='start_date',
        lookup_type='lte')
    min_end_date = django_filters.DateTimeFilter(
        name='end_date',
        lookup_type='gte')
    max_end_date = django_filters.DateTimeFilter(
        name='end_date',
        lookup_type='lte')

    class Meta:
        model = Network
        fields = [
            'name',
            'code',
            'start_date',
            'end_date',
            'min_start_date',
            'max_start_date',
            'min_end_date',
            'max_end_date',
            'restricted_status',
            'alternate_code',
            'historical_code',
        ]


class ChannelDatatypeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='type_description')

    class Meta:
        model = DataType
        fields = [
            'name',
        ]


class ChannelFilter(django_filters.FilterSet):
    """
    Enables filter on Chanels.
    """
    station = django_filters.CharFilter(name='station__station_code')
    network = django_filters.CharFilter(name='network__network_code')
    code = django_filters.CharFilter(name='channel_code')
    min_start_date = django_filters.DateTimeFilter(
        name='start_date',
        lookup_type='gte')
    max_start_date = django_filters.DateTimeFilter(
        name='start_date',
        lookup_type='lte')
    min_end_date = django_filters.DateTimeFilter(
        name='end_date',
        lookup_type='gte')
    max_end_date = django_filters.DateTimeFilter(
        name='end_date',
        lookup_type='lte')
    datatype = django_filters.CharFilter(name='data_type__type_description')

    class Meta:
        model = Channel
        fields = [
            'station',
            'network',
            'location_code',
            'code',
            'start_date',
            'end_date',
            'min_start_date',
            'max_start_date',
            'min_end_date',
            'max_end_date',
            'restricted_status',
            'alternate_code',
            'historical_code',
            'latitude_unit',
            'latitude',
            'longitude_unit',
            'longitude',
            'elevation_unit',
            'elevation',
            'depth_unit',
            'depth',
            'azimuth_unit',
            'azimuth',
            'dip',
            'dip_unit',
            'sample_rate',
            'sample_rate_unit',
            'storage_format',
            'clock_drift',
            'clock_drift_unit',
            'datatype',
        ]


class CalibrationUnitFilter(django_filters.FilterSet):
    class Meta:
        model = CalibrationUnit
        fields = [
            'name',
            'description',
        ]


class EquipmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(name='equip_model__equip_model_name')
    type = django_filters.CharFilter(name='equip_model__equip_type__equip_type_name')
    station = django_filters.CharFilter(name='last_station__station_code')
    manufacturer = django_filters.CharFilter(name='equip_model__manufacturer')

    class Meta:
        model = Equipment
        fields = [
            'name',
            'type',
            'serial_number',
            'manufacturer',
            'station',
        ]


class ServiceFilter(django_filters.FilterSet):
    equipment = django_filters.NumberFilter(name='equipment__id')

    class Meta:
        model = Service
        fields = [
            'protocol',
            'equipment',
        ]


class IPAddressFilter(django_filters.FilterSet):
    equipment = django_filters.NumberFilter(name='equipment__id')

    class Meta:
        model = IPAddress
        fields = [
            'ip',
            'equipment',
        ]


class ChainFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(
        name='order',
        choices=Chain.ORDER_CHOICES)

    class Meta:
        model = Chain
        fields = [
            'type',
        ]
