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

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class ChannelViewSet(viewsets.ModelViewSet):
    """
    List of channels.
    """
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class DatatypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of datatypes.

    Used by:

      * channels
    """
    serializer_class = DatatypeSerializer
    queryset = Datatype.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class DocumentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of documents types.

    Used by:

      * documents
    """
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


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

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class EquipmentConfigurationViewSet(viewsets.ModelViewSet):
    """
    Each parameter/value pair from a given equipment.
    """
    serializer_class = EquipmentConfigurationSerializer
    queryset = Configuration.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class EquipmentStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Previous and current state an equipment had or have.
    """
    serializer_class = EquipmentStateSerializer
    queryset = EquipmentState.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class EquipmentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of equipment model's types.

    Used by:

      * equipment's model
    """
    serializer_class = EquipmentTypeSerializer
    queryset = Type.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class EquipmentModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of equipment's models.

    Used by:

      * equipments
    """
    serializer_class = EquipmentModelSerializer
    queryset = Model.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class EquipmentViewSet(viewsets.ModelViewSet):
    """
    List of equipments.
    """
    serializer_class = EquipmentSerializer
    queryset = Equipment.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class ForbiddenEquipmentModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of forbidden equipment's model.

    It defines which model shouldn't permit to create new equipments. And gives
    which model we should use instead.

    For an example, if 'original' is 'STS-1 Gen 3' and recommended is 'STS-1',
    then it means you must create 'STS-1' equipments instead of 'STS -1 Gen 3'
    """
    serializer_class = ForbiddenEquipmentModelSerializer
    queryset = ForbiddenEquipmentModel.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class GroundTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of ground types.

    Used by:

      * places
    """
    serializer_class = GroundTypeSerializer
    queryset = GroundType.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class IPAddressViewSet(viewsets.ModelViewSet):
    """
    List of used IP address. This is linked to an equipment.
    """
    serializer_class = IPAddressSerializer
    queryset = IPAddress.objects.all()

    permission_classes = (permissions.DjangoModelPermissions,)


class InstallationViewSet(viewsets.ModelViewSet):
    """
    When you install an equipment somewhere, you give some details about it.

    Here is the list of all equipment's installations.
    """
    serializer_class = InstallationSerializer
    queryset = Installation.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class NetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of networks.
    """
    serializer_class = NetworkSerializer
    queryset = Network.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class ParameterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of parameters a equipment's model have.
    """
    serializer_class = ParameterSerializer
    queryset = Parameter.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class PlaceViewSet(viewsets.ModelViewSet):
    """
    List of places.
    """
    serializer_class = PlaceSerializer
    queryset = Place.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class PlaceStateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Previous and current state a place had or have.
    """
    serializer_class = PlaceStateSerializer
    queryset = PlaceState.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of projects. Regroup users.
    """
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    List of available services on a given equipment.
    """
    serializer_class = ServiceSerializer
    queryset = Service.objects.all()

    permission_classes = (permissions.DjangoModelPermissions,)


class StationViewSet(viewsets.ModelViewSet):
    """
    List of stations.
    """
    serializer_class = StationSerializer
    queryset = Station.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of users.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

    permission_classes = (permissions.IsAuthenticated,)


class ValueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List of values linked to a specific parameter (itself linked to a given
    equipment's model)
    """
    serializer_class = ValueSerializer
    queryset = Value.objects.all()

    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
