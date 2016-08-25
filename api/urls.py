from rest_framework import routers

from api import views

# REST FRAMEWORK API
v2_router = routers.DefaultRouter()

v2_router = routers.DefaultRouter()
v2_router.register(r'agency', views.AgencyViewSet)
v2_router.register(r'channel', views.ChannelViewSet)
v2_router.register(r'datatype', views.DatatypeViewSet)
v2_router.register(r'document', views.DocumentViewSet)
v2_router.register(
    r'document_type',
    views.DocumentTypeViewSet,
    base_name='document_type')
v2_router.register(r'equipment', views.EquipmentViewSet)
v2_router.register(
    r'equipment_configuration',
    views.EquipmentConfigurationViewSet,
    base_name='equipment_configuration')
v2_router.register(
    r'equipment_state',
    views.EquipmentStateViewSet,
    base_name='equipment_state')
v2_router.register(
    r'forbidden_model',
    views.ForbiddenEquipmentModelViewSet,
    base_name='forbidden_model')
v2_router.register(
    r'ground_type',
    views.GroundTypeViewSet,
    base_name='ground_type')
v2_router.register(r'installation', views.InstallationViewSet)
v2_router.register(r'ip', views.IPAddressViewSet, base_name='ip')
v2_router.register(r'model', views.EquipmentModelViewSet)
v2_router.register(r'network', views.NetworkViewSet)
v2_router.register(r'parameter', views.ParameterViewSet)
v2_router.register(r'place', views.PlaceViewSet)
v2_router.register(
    r'place_state',
    views.PlaceStateViewSet,
    base_name='place_state')
v2_router.register(r'project', views.ProjectViewSet)
v2_router.register(r'service', views.ServiceViewSet)
v2_router.register(r'station', views.StationViewSet)
v2_router.register(r'type', views.EquipmentTypeViewSet)
v2_router.register(r'user', views.UserViewSet)
v2_router.register(r'value', views.ValueViewSet)

urlpatterns = v2_router.urls
