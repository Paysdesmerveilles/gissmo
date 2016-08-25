# -*- coding: utf-8 -*-

from affiliation.models import Agency
from affiliation.types import TYPE_CHOICES as AGENCY_TYPE_CHOICES

from django.contrib.auth.models import User, Group

from document.models import Document
from document.models import Type as DocumentType

from equipment.models import (
    Configuration,
    Equipment,
    ForbiddenEquipmentModel,
    IPAddress,
    Model,
    Parameter,
    Service,
    Type,
    Value,
)
from equipment.models import State as EquipmentState
from equipment.types import TYPE_CHOICES as INSTALLATION_TYPE_CHOICES

from network.models import (
    Channel,
    Datatype,
    Installation,
    Network,
    Station,
)

from place.models import GroundType, Place
from place.models import State as PlaceState
from place.types import TYPE_CHOICES as PLACE_TYPE_CHOICES

from project.models import Project

from rest_framework import serializers


class AgencySerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.ChoiceField(choices=AGENCY_TYPE_CHOICES, source='_type')

    class Meta:
        model = Agency
        fields = (
            'id',
            'name',
            'type',
            'parent',
            'users',
        )


class ChannelSerializer(serializers.HyperlinkedModelSerializer):
    configurations = serializers.HyperlinkedRelatedField(
        view_name='equipment_configuration-detail',
        read_only=True,
        many=True)

    class Meta:
        model = Channel
        fields = (
            'id',
            'installation',
            'station',
            'network',
            'code',
            'location_code',
            'azimuth',
            'dip',
            'sample_rate',
            'start',
            'end',
            'description',
            'calibration_unit',
            'latitude',
            'longitude',
            'elevation',
            'datatypes',
            'configurations',
        )


class DatatypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Datatype
        fields = (
            'id',
            'name',
        )


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.HyperlinkedRelatedField(
        source='_type',
        view_name='document_type-detail',
        queryset=DocumentType.objects.all())
    file = serializers.FileField(source='_file')
    class Meta:
        model = Document
        fields = (
            'id',
            'type',
            'owner',
            'title',
            'date',
            'private_link',
            'start',
            'end',
            'file',
        )


class DocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentType
        fields = (
            'id',
            'name',
        )


class EquipmentSerializer(serializers.HyperlinkedModelSerializer):
    state = serializers.HyperlinkedRelatedField(
        view_name='equipment_state-detail',
        read_only=True)

    class Meta:
        model = Equipment
        fields = (
            'id',
            'name',
            'model',
            'owner',
            'place',
            'vendor',
            'contact',
            'purchase_date',
            'clock_drift',
            'clock_drift_unit',
            'storage_format',
            'note',
            'state',
            'last_user',
            'last_edition',
            'documents',
        )


class EquipmentConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Configuration
        fields = (
            'id',
            'parameter',
            'value',
            'start',
            'end',
            'equipment',
        )


class EquipmentModelSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.HyperlinkedRelatedField(
        source='_type',
        view_name='type-detail',
        queryset=Type.objects.all())

    class Meta:
        model = Model
        fields = (
            'id',
            'name',
            'rank',
            'manufacturer',
            'type',
            'chain_type',
            'is_network_model',
            'documents',
        )


class EquipmentStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EquipmentState
        fields = (
            'id',
            'code',
            'start',
            'end',
            'equipment',
        )


class EquipmentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Type
        fields = (
            'id',
            'name',
            'rank',
            'parent',
        )


class ForbiddenEquipmentModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ForbiddenEquipmentModel
        fields = (
            'id',
            'original',
            'recommended',
        )


class GroundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroundType
        fields = (
            'id',
            'name',
            'description',
        )


class IPAddressSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IPAddress
        fields = (
            'id',
            'ip',
            'netmask',
            'equipment',
        )


class InstallationSerializer(serializers.HyperlinkedModelSerializer):
    start = serializers.DateTimeField()
    type = serializers.ChoiceField(
        choices=INSTALLATION_TYPE_CHOICES,
        source='_type')
    configurations = serializers.HyperlinkedRelatedField(
        view_name='equipment_configuration-detail',
        read_only=True,
        many=True)

    class Meta:
        model = Installation
        fields = (
            'id',
            'parent',
            'equipment',
            'place',
            'type',
            'start',
            'end',
            'depth',
            'latitude',
            'longitude',
            'elevation',
            'configurations',
        )


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = (
            'id',
            'code',
            'name',
            'description',
            'start',
            'end',
        )


class ParameterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Parameter
        fields = (
            'id',
            'name',
            'model',
        )


class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.ChoiceField(choices=PLACE_TYPE_CHOICES, source='_type')
    state = serializers.HyperlinkedRelatedField(
        view_name='place_state-detail',
        read_only=True)

    class Meta:
        model = Place
        fields = (
            'id',
            'name',
            'type',
            'description',
            'creation_date',
            'note',
            'state',
            'address_street',
            'address_zipcode',
            'address_city',
            'address_region',
            'address_county',
            'address_country',
            'geology',
            'ground_type',
            'contact',
            'latitude',
            'longitude',
            'elevation',
            'operators',
            'documents',
        )


class PlaceStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PlaceState
        fields = (
            'id',
            'code',
            'start',
            'end',
            'place',
        )


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'manager',
            'places',
        )


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Service
        fields = (
            'id',
            'protocol',
            'port',
            'description',
            'equipment',
        )


class StationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Station
        fields = (
            'id',
            'code',
            'description',
            'state',
            'latitude',
            'longitude',
            'elevation',
            'documents',
            'places',
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        )


class ValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Value
        fields = (
            'id',
            'name',
            'is_default',
            'parameter',
        )

# network_built (link between station and place) => needed or not?

# TODO: Add functions/method to add:
#  - an operator on a place
#  - a document on a place
#  - a user in a project
#  - a document on an equipment's model
#  - a document on an equipment
#  - a document on a station
#  - a configuration to an installation
#  - a configuration to a channel
#  - a datatype to a channel
#  - a possibility to see link between users and project
