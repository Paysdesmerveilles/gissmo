# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import (
    filters,
    viewsets,
)

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

from api.serializers import (
    CalibrationUnitSerializer,
    ChainSerializer,
    ChannelDatatypeSerializer,
    ChannelParameterSerializer,
    ChannelSerializer,
    DocumentSerializer,
    EquipmentSerializer,
    IPAddressSerializer,
    NetworkSerializer,
    OrganismSerializer,
    ServiceSerializer,
    SiteSerializer,
)

from api.filters import (
    ChainFilter,
    ChannelDatatypeFilter,
    ChannelFilter,
    ChannelParameterFilter,
    EquipmentFilter,
    IPAddressFilter,
    NetworkFilter,
    OrganismFilter,
    ServiceFilter,
    SiteFilter,
)


class OrganismViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Network, Observatories, Business, etc. that are:

      * station operator
      * equipment owner
      * organism that perform an action during an intervention
    """
    serializer_class = OrganismSerializer
    queryset = Organism.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_class = OrganismFilter
    search_fields = ['name']


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
    queryset = Channel.objects.all().prefetch_related(
        'channel_code',
        'station',
        'network',
        'data_type',
        'calibration_units',
        'chain_set__channel',
        'chain_set__equip__equip_model',
        'equipments__equip_model__equip_type')
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
    ordering_fields = ['name']
    ordering = ['name']


class EquipmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Gissmo registered equipments from years.
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all().prefetch_related(
        'equip_model__equip_type',
        'last_station')
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


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Available services linked to a specific equipment.
    """
    serializer_class = ServiceSerializer
    queryset = Service.objects.all().prefetch_related('equipment')
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,)
    filter_class = ServiceFilter
    search_fields = ['protocol']


class IPAddressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Available IP linked to a specific equipment.
    """
    serializer_class = IPAddressSerializer
    queryset = IPAddress.objects.all().prefetch_related('equipment')
    filter_backends = (
        filters.DjangoFilterBackend,)
    filter_class = IPAddressFilter


class ChainViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Acquisition Chain that link a canal to a given equipment.
    By searching all chains linked to a given canal, you will have it's
    acquisition chain.
    """
    serializer_class = ChainSerializer
    queryset = Chain.objects.all()
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,)
    filter_class = ChainFilter
    search_fields = ['type']


class ChannelParameterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Each channel have some specific parameters needed to understand how
    read the signal.
    This view informs you which parameter each channel owns.
    """
    serializer_class = ChannelParameterSerializer
    queryset = ChainConfig.objects.all().prefetch_related(
        'parameter__equip_model',
        'value',
        'channel')
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,)
    filter_class = ChannelParameterFilter
    search_fields = ['parameter']


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Documents.
    """
    serializer_class = DocumentSerializer
    queryset = DocumentView.objects.all()
