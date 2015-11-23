# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from gissmo.models import (
    Actor,
    CalibrationUnit,
    Channel,
    DataType,
    Network,
    StationSite)

from rest_framework import serializers


class EnumField(serializers.ChoiceField):
    """
    Print choice string instead of its number.
    """
    def to_representation(self, obj):
        res = obj
        for key, value in self.choices.items():
            if key == obj:
                res = value
                break
        return res


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='actor_name')
    type = EnumField(choices=Actor.ACTOR_TYPE_CHOICES, source='actor_type')

    class Meta:
        model = Actor
        fields = (
            'id',
            'name',
            'type',
        )


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='site_name')
    code = serializers.CharField(source='station_code')
    type = EnumField(choices=StationSite.SITE_CHOICES, source='site_type', label='Type')
    restricted_status = EnumField(choices=StationSite.STATUS)

    class Meta:
        model = StationSite
        fields = (
            'id',
            'name',
            'code',
            'type',
            'restricted_status',
            'alternate_code',
            'historical_code',
            'latitude_unit',
            'longitude_unit',
            'elevation_unit',
            'longitude',
            'latitude',
            'elevation',
            'town',
            'county',
            'region',
            'country',
            'region',
            # 'vault',  # missing field in station_xml
            'geology',
            'operator',
        )


class NetworkSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='network_name')
    code = serializers.CharField(source='network_code')
    restricted_status = EnumField(choices=Network.STATUS)

    class Meta:
        model = Network
        fields = [
            'id',
            'name',
            'code',
            'start_date',
            'end_date',
            'restricted_status',
            'alternate_code',
            'historical_code',
            'description',
        ]


class ChannelDatatypeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='type_description')

    class Meta:
        model = DataType
        fields = [
            'id',
            'name',
        ]


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    code = serializers.CharField(source='channel_code')
    datatypes = serializers.StringRelatedField(many=True, source='data_type')

    class Meta:
        model = Channel
        fields = [
            'id',
            'station',
            'network',
            'location_code',
            'code',
            'start_date',
            'end_date',
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
            'calibration_units',
            'datatypes',
        ]


class CalibrationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationUnit
        fields = [
            'id',
            'name',
            'description',
        ]
