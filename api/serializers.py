# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from gissmo.models import (
    CalibrationUnit,
    Chain,
    ChainConfig,
    Channel,
    DataType,
    DocumentView,
    Equipment,
    IPAddress,
    Network,
    Organism,
    Service,
    StationSite,
)

from equipment.protocols import PROTOCOL_CHOICES
from equipment.states import EQUIP_STATES

from station.states import STATION_STATES

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


class OrganismSerializer(serializers.HyperlinkedModelSerializer):
    type = EnumField(
        choices=Organism.ORGANISM_TYPE_CHOICES,
        source='_type')

    class Meta:
        model = Organism
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
    status = EnumField(choices=STATION_STATES, source='last_state')

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
            'status',
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
    chains = serializers.HyperlinkedRelatedField(
        source='chain_set',
        view_name='chain-detail',
        read_only=True,
        many=True)

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
            'equipments',
            'chains',
        ]


class CalibrationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalibrationUnit
        fields = [
            'id',
            'name',
            'description',
        ]


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='equip_model')
    type = serializers.CharField(source='equip_type')
    station = serializers.HyperlinkedRelatedField(
        source='last_station',
        view_name='stationsite-detail',
        read_only=True)
    manufacturer = serializers.CharField(source='equip_model.manufacturer')
    status = EnumField(choices=EQUIP_STATES, source='last_state')

    class Meta:
        model = Equipment
        fields = [
            'id',
            'name',
            'type',
            'serial_number',
            'manufacturer',
            'station',
            'status',
        ]


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    protocol = EnumField(choices=PROTOCOL_CHOICES)

    class Meta:
        model = Service
        fields = [
            'protocol',
            'port',
            'description',
            'equipment',
        ]


class IPAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IPAddress
        fields = [
            'ip',
            'netmask',
            'equipment',
        ]


class ChainSerializer(serializers.HyperlinkedModelSerializer):
    type = EnumField(choices=Chain.ORDER_CHOICES, source='order')
    equipment = serializers.HyperlinkedRelatedField(
        source='equip',
        view_name='equipment-detail',
        read_only=True)

    class Meta:
        model = Chain
        fields = [
            'id',
            'type',
            'channel',
            'equipment',
        ]


class ChannelParameterSerializer(serializers.HyperlinkedModelSerializer):
    parameter = serializers.CharField(source='parameter.parameter_name')
    value = serializers.CharField(source='value.value')
    model = serializers.CharField(
        source='parameter.equip_model.equip_model_name')

    class Meta:
        model = ChainConfig
        fields = [
            'channel',
            'parameter',
            'value',
            'model',
        ]


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    linked_to = serializers.CharField(source='model')
    link = serializers.FileField(source='_file')
    doctype = serializers.CharField(source='_type')
    intervention_id = serializers.IntegerField(source='intervention')

    class Meta:
        model = DocumentView
        fields = [
            'linked_to',
            'title',
            'doctype',
            'start',
            'end',
            'link',
            'equipment',
            'station',
            'equipmodel',
            'intervention_id',
        ]
