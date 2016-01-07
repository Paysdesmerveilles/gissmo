from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from gissmo import views

from api import views as api_views

from rest_framework import routers

# Admin configuration
admin.autodiscover()
admin.site.site_header = 'Gissmo'
admin.site.site_title = 'Gissmo'
admin.site.site_url = '/gissmo'

# REST FRAMEWORK API
apirouter = routers.DefaultRouter()
apirouter.register(r'actors', api_views.ActorViewSet)
apirouter.register(r'calibration_units', api_views.CalibrationUnitViewSet)
apirouter.register(r'chains', api_views.ChainViewSet)
apirouter.register(r'channel_datatypes', api_views.ChannelDatatypeViewSet)
apirouter.register(r'channel_parameters', api_views.ChannelParameterViewSet)
apirouter.register(r'channels', api_views.ChannelViewSet)
apirouter.register(r'equipments', api_views.EquipmentViewSet)
apirouter.register(r'ipaddresses', api_views.IPAddressViewSet)
apirouter.register(r'networks', api_views.NetworkViewSet)
apirouter.register(r'services', api_views.ServiceViewSet)
apirouter.register(r'sites', api_views.SiteViewSet)

urlpatterns = [
    url(r'^gissmo/xhr_station$',
        views.xhr_station,
        name='xhr_station'),
    url(r'^gissmo/xhr_station_state$',
        views.xhr_station_state,
        name='xhr_station_state'),
    url(r'^gissmo/xhr_equipment$',
        views.xhr_equipment,
        name='xhr_equipment'),
    url(r'^gissmo/xhr_equip_state$',
        views.xhr_equip_state,
        name='xhr_equip_state'),
    url(r'^gissmo/xhr_equip_oper$',
        views.xhr_equip_oper,
        name='xhr_equip_oper'),
    url(r'^gissmo/xhr_station_position$',
        views.xhr_station_position,
        name='xhr_station_position'),
    url(r'^gissmo/xhr_built$',
        views.xhr_built,
        name='xhr_built'),
    url(r'^gissmo/xhr_parameter_value$',
        views.xhr_parameter_value,
        name='xhr_parameter_value'),
    url(r'^gissmo/site_maps/$',
        views.site_maps,
        name='site_maps'),
    url(r'^gissmo/itineraire_maps/$',
        views.itineraire_maps,
        name='itineraire_maps'),
    url(r'^gissmo/dataless/$',
        views.dataless,
        name='dataless'),
    url(r'^gissmo/get_file/(?P<app_label>.+)/(?P<model_name>.+)/(?P<field_name>.+)/(?P<identifier>\d+)$',
        views.get_file,
        name='get_file'),
    url(r'^gissmo/station_xml/$',
        views.station_xml,
        name='station_xml'),
    url(r'^gissmo/network_xml/$',
        views.network_xml,
        name='network_xml'),
    url(r'^gissmo/station_dataless/$',
        views.station_dataless,
        name='station_dataless'),
    url(r'^gissmo/([A-Z0-9]{2,4})/$',
        views.site_shortcut,
        name='site_shortcut'),
    url(r'^gissmo/', include(admin.site.urls)),
    url(r'^autocomplete/', include('autocomplete_light.urls')),
    url(r'^api/', include(apirouter.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Note about STATIC_URL: django.contrib.staticfils in INSTALLED_APPS do the job
