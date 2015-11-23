# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import (
    filters,
    viewsets)


from gissmo.models import (
    Actor,
    CalibrationUnit,
    Channel,
    DataType,
    Equipment,
    Network,
    StationSite,
)

from api.serializers import (
    ActorSerializer,
    CalibrationUnitSerializer,
    ChannelSerializer,
    ChannelDatatypeSerializer,
    EquipmentSerializer,
    NetworkSerializer,
    SiteSerializer)

from api.filters import (
    ActorFilter,
    CalibrationUnitFilter,
    ChannelFilter,
    ChannelDatatypeFilter,
    EquipmentFilter,
    NetworkFilter,
    SiteFilter)


class ActorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    All kind of actors used for:

      * buying equipment
      * equipment creator
      * site owner
      * users
    """
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_class = ActorFilter
    search_fields = ['actor_name']


class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Main data about sites:

      * Sites
      * Stations
      * Theoritical stations
      * Observatories
    """
    serializer_class = SiteSerializer
    queryset = StationSite.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_class = SiteFilter
    search_fields = ['station_code', 'site_name']


class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of networks.
    """
    serializer_class = NetworkSerializer
    queryset = Network.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,)
    filter_class = NetworkFilter
    search_fields = ['network_code']
    ordering_fields = ['network_code']
    ordering = ['network_code']


class ChannelDatatypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    The type of data a channel collects.

    [Available types](https://github.com/FDSN/StationXML/blob/master/fdsn-station.xsd#L276)
    """
    serializer_class = ChannelDatatypeSerializer
    queryset = DataType.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,)
    filter_class = ChannelDatatypeFilter
    search_fields = ['type_description']
    ordering_fields = ['type_description']
    ordering = ['type_description']


class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    All known channels in GISSMO without any filtering.
    """
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,)
    filter_class = ChannelFilter
    search_fields = ['channel_code__channel_code']
    ordering_fields = ['station__station_code']


class CalibrationUnitViewSet(viewsets.ReadOnlyModelViewSet):
    """
    All kind of Calibration Unit used by Channels.
    """
    serializer_class = CalibrationUnitSerializer
    queryset = CalibrationUnit.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,)
    filter_class = CalibrationUnitFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Gissmo registered equipments from years.
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,)
    filter_class = EquipmentFilter
    search_fields = [
        'equip_model__equip_model_name',
        'equip_model__equip_type__equip_type_name',
        'serial_number',
    ]
    ordering_fields = ['equip_model__equip_model_name', 'serial_number']
    ordering = ['equip_model__equip_model_name']
