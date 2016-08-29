# -*- coding: utf-8 -*-
from affiliation.models import Agency

from api.serializers import (
    AgencySerializer,
    ChannelSerializer,
    DatatypeSerializer,
    DocumentSerializer,
    DocumentTypeSerializer,
    EquipmentConfigurationSerializer,
    EquipmentModelSerializer,
    EquipmentSerializer,
    EquipmentStateSerializer,
    EquipmentTypeSerializer,
    ForbiddenEquipmentModelSerializer,
    GroundTypeSerializer,
    IPAddressSerializer,
    InstallationSerializer,
    NetworkSerializer,
    ParameterSerializer,
    PlaceSerializer,
    PlaceStateSerializer,
    ProjectSerializer,
    ServiceSerializer,
    StationSerializer,
    UserSerializer,
    ValueSerializer,
)

from django.contrib.auth.models import User

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

from network.models import (
    Channel,
    Datatype,
    Installation,
    Network,
    Station,
)

from place.models import GroundType, Place
from place.models import State as PlaceState

from project.models import Project

from rest_framework import viewsets, permissions


class AgencyViewSet(viewsets.ModelViewSet):
    """
    List of agencies.
    """
    serializer_class = AgencySerializer
    queryset = Agency.objects.all()


class ChannelViewSet(viewsets.ModelViewSet):
    """
    List of channels.
    """
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()


class DatatypeViewSet(viewsets.ModelViewSet):
    """
    List of datatypes.

    Used by:

      * channels
    """
    serializer_class = DatatypeSerializer
    queryset = Datatype.objects.all()


class DocumentTypeViewSet(viewsets.ModelViewSet):
    """
    List of documents types.

    Used by:

      * documents
    """
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()


class DocumentViewSet(viewsets.ModelViewSet):
    """
    List of documents.

    Used by:

      * places
      * equipment's models
      * equipments
      * stations
    """
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()


class EquipmentConfigurationViewSet(viewsets.ModelViewSet):
    """
    Each parameter/value pair from a given equipment.
    """
    serializer_class = EquipmentConfigurationSerializer
    queryset = Configuration.objects.all()


class EquipmentStateViewSet(viewsets.ModelViewSet):
    """
    Previous and current state an equipment had or have.
    """
    serializer_class = EquipmentStateSerializer
    queryset = EquipmentState.objects.all()


class EquipmentTypeViewSet(viewsets.ModelViewSet):
    """
    List of equipment model's types.

    Used by:

      * equipment's model
    """
    serializer_class = EquipmentTypeSerializer
    queryset = Type.objects.all()


class EquipmentModelViewSet(viewsets.ModelViewSet):
    """
    List of equipment's models.

    Used by:

      * equipments
    """
    serializer_class = EquipmentModelSerializer
    queryset = Model.objects.all()


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    List of equipments.
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()


class ForbiddenEquipmentModelViewSet(viewsets.ModelViewSet):
    """
    List of forbidden equipment's model.

    It defines which model shouldn't permit to create new equipments. And gives
    which model we should use instead.

    For an example, if 'original' is 'STS-1 Gen 3' and recommended is 'STS-1',
    then it means you must create 'STS-1' equipments instead of 'STS -1 Gen 3'
    """
    serializer_class = ForbiddenEquipmentModelSerializer
    queryset = ForbiddenEquipmentModel.objects.all()


class GroundTypeViewSet(viewsets.ModelViewSet):
    """
    List of ground types.

    Used by:

      * places
    """
    serializer_class = GroundTypeSerializer
    queryset = GroundType.objects.all()


class IPAddressViewSet(viewsets.ModelViewSet):
    """
    List of used IP address. This is linked to an equipment.
    """
    serializer_class = IPAddressSerializer
    queryset = IPAddress.objects.all()

    permission_classes = (permissions.IsAuthenticated,)


class InstallationViewSet(viewsets.ModelViewSet):
    """
    When you install an equipment somewhere, you give some details about it.

    Here is the list of all equipment's installations.
    """
    serializer_class = InstallationSerializer
    queryset = Installation.objects.all()


class NetworkViewSet(viewsets.ModelViewSet):
    """
    List of networks.
    """
    serializer_class = NetworkSerializer
    queryset = Network.objects.all()


class ParameterViewSet(viewsets.ModelViewSet):
    """
    List of parameters a equipment's model have.
    """
    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()


class PlaceViewSet(viewsets.ModelViewSet):
    """
    List of places.
    """
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()


class PlaceStateViewSet(viewsets.ModelViewSet):
    """
    Previous and current state a place had or have.
    """
    serializer_class = PlaceStateSerializer
    queryset = PlaceState.objects.all()


class ProjectViewSet(viewsets.ModelViewSet):
    """
    List of projects. Regroup users.
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()


class ServiceViewSet(viewsets.ModelViewSet):
    """
    List of available services on a given equipment.
    """
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()

    permission_classes = (permissions.IsAuthenticated,)


class StationViewSet(viewsets.ModelViewSet):
    """
    List of stations.
    """
    serializer_class = StationSerializer
    queryset = Station.objects.all()


class UserViewSet(viewsets.ModelViewSet):
    """
    List of users.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    permission_classes = (permissions.IsAuthenticated,)


class ValueViewSet(viewsets.ModelViewSet):
    """
    List of values linked to a specific parameter (itself linked to a given
    equipment's model)
    """
    serializer_class = ValueSerializer
    queryset = Value.objects.all()
