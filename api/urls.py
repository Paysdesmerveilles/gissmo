from rest_framework import routers

from api import views

# REST FRAMEWORK API
v2_router = routers.DefaultRouter()

v2_router = routers.DefaultRouter()
v2_router.register(r'agencies', views.AgencyViewSet)
v2_router.register(r'channels', views.ChannelViewSet)
v2_router.register(r'datatypes', views.DatatypeViewSet)
v2_router.register(r'documents', views.DocumentViewSet)
v2_router.register(
    r'document_types',
    views.DocumentTypeViewSet,
    base_name='document_types')
v2_router.register(r'equipments', views.EquipmentViewSet)
v2_router.register(
    r'equipment_configurations',
    views.EquipmentConfigurationViewSet,
    base_name='equipment_configurations')
v2_router.register(
    r'equipment_states',
    views.EquipmentStateViewSet,
    base_name='equipment_states')
v2_router.register(
    r'forbidden_models',
    views.ForbiddenEquipmentModelViewSet,
    base_name='forbidden_models')
v2_router.register(
    r'ground_types',
    views.GroundTypeViewSet,
    base_name='ground_types')
v2_router.register(r'installations', views.InstallationViewSet)
v2_router.register(r'ips', views.IPAddressViewSet, base_name='ip')
v2_router.register(r'models', views.EquipmentModelViewSet)
v2_router.register(r'networks', views.NetworkViewSet)
v2_router.register(r'parameters', views.ParameterViewSet)
v2_router.register(r'places', views.PlaceViewSet)
v2_router.register(
    r'place_states',
    views.PlaceStateViewSet,
    base_name='place_states')
v2_router.register(r'projects', views.ProjectViewSet, base_name='projects')
v2_router.register(r'services', views.ServiceViewSet)
v2_router.register(r'stations', views.StationViewSet)
v2_router.register(r'types', views.EquipmentTypeViewSet, base_name='types')
v2_router.register(r'users', views.UserViewSet)
v2_router.register(r'values', views.ValueViewSet)

urlpatterns = v2_router.urls
