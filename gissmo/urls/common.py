from django.conf.urls.defaults import include, patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'gissmo.views',
    url(r'^xhr_station$', 'xhr_station', name='xhr_station'),
    url(r'^xhr_station_state$', 'xhr_station_state', name='xhr_station_state'),
    url(r'^xhr_equipment$', 'xhr_equipment', name='xhr_equipment'),
    url(r'^xhr_equip_state$', 'xhr_equip_state', name='xhr_equip_state'),
    url(r'^xhr_equip_oper$', 'xhr_equip_oper', name='xhr_equip_oper'),
    url(r'^xhr_station_position$', 'xhr_station_position', name='xhr_station_position'),
    url(r'^xhr_built$', 'xhr_built', name='xhr_built'),
    url(r'^xhr_parameter_value$', 'xhr_parameter_value', name='xhr_parameter_value'),
    url(r'^site_maps/$', 'site_maps', name='site_maps'),
    url(r'^itineraire_maps/$', 'itineraire_maps', name='itineraire_maps'),
    url(r'^dataless/$', 'dataless', name='dataless'),
    url(r'^get_file/(?P<app_label>.+)/(?P<model_name>.+)/(?P<field_name>.+)/(?P<identifier>\d+)$', 'get_file', name='get_file'),
    url(r'^station_xml/$', 'station_xml', name='station_xml'),
    url(r'^network_xml/$', 'network_xml', name='network_xml'),
    url(r'^station_dataless/$', 'station_dataless', name='station_dataless'),
    url(r'^test_site/$', 'test_site', name='test_site'),
    (r'^admin/', include(admin.site.urls)),
    (r'^chaining/', include('smart_selects.urls')),
)
