# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from gissmo.models import (
    Organism,
    Chain,
    ChainConfig,
    Channel,
    DataType,
    Equipment,
    IPAddress,
    Network,
    Service,
    StationSite,
)

import django_filters


class OrganismFilter(django_filters.FilterSet):
    """
    Enables filtering on Organism.
    """
    class Meta:
        model = Organism
        fields = ['name']


class SiteFilter(django_filters.FilterSet):
    """
    Enables filtering on Site.
    """
    code = django_filters.CharFilter(name="station_code")
    restricted_status = django_filters.ChoiceFilter(
        choices=StationSite.STATUS)

    class Meta:
        model = StationSite
        fields = [
            'code',
        ]


class NetworkFilter(django_filters.FilterSet):
    """
    Enables filtering on Network.
    """
    code = django_filters.CharFilter(name='network_code')
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
            'code',
            'start_date',
            'end_date',
            'min_start_date',
            'max_start_date',
            'min_end_date',
            'max_end_date',
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

    class Meta:
        model = Channel
        fields = [
            'station',
            'code',
            'start_date',
            'end_date',
            'min_start_date',
            'max_start_date',
            'min_end_date',
            'max_end_date',
        ]


class EquipmentFilter(django_filters.FilterSet):
    type = django_filters.CharFilter(name='equip_model__equip_type__equip_type_name')
    station = django_filters.CharFilter(name='last_station__station_code')

    class Meta:
        model = Equipment
        fields = [
            'type',
            'station',
        ]


class ServiceFilter(django_filters.FilterSet):
    equipment = django_filters.NumberFilter(name='equipment__id')

    class Meta:
        model = Service
        fields = [
            'equipment',
        ]


class IPAddressFilter(django_filters.FilterSet):
    equipment = django_filters.NumberFilter(name='equipment__id')

    class Meta:
        model = IPAddress
        fields = [
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


class ChannelParameterFilter(django_filters.FilterSet):
    channel = django_filters.NumberFilter(name='channel__id')

    class Meta:
        model = ChainConfig
        fields = [
            'channel',
        ]
