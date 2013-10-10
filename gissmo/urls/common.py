from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'gissmo.views',
    url(r'^gissmo/xhr_station$', 'xhr_station', name='xhr_station'),
    url(r'^gissmo/xhr_station_state$', 'xhr_station_state', name='xhr_station_state'),
    url(r'^gissmo/xhr_equipment$', 'xhr_equipment', name='xhr_equipment'),
    url(r'^gissmo/xhr_equip_state$', 'xhr_equip_state', name='xhr_equip_state'),
    url(r'^gissmo/xhr_equip_oper$', 'xhr_equip_oper', name='xhr_equip_oper'),
    url(r'^gissmo/xhr_station_position$', 'xhr_station_position', name='xhr_station_position'),
    url(r'^gissmo/xhr_built$', 'xhr_built', name='xhr_built'),
    url(r'^gissmo/xhr_parameter_value$', 'xhr_parameter_value', name='xhr_parameter_value'),
    url(r'^gissmo/site_maps/$', 'site_maps', name='site_maps'),
    url(r'^gissmo/itineraire_maps/$', 'itineraire_maps', name='itineraire_maps'),
    url(r'^gissmo/dataless/$', 'dataless', name='dataless'),
    url(r'^gissmo/get_file/(?P<app_label>.+)/(?P<model_name>.+)/(?P<field_name>.+)/(?P<identifier>\d+)$', 'get_file', name='get_file'),
    url(r'^gissmo/station_xml/$', 'station_xml', name='station_xml'),
    url(r'^gissmo/network_xml/$', 'network_xml', name='network_xml'),
    url(r'^gissmo/station_dataless/$', 'station_dataless', name='station_dataless'),
    url(r'^gissmo/test_site/$', 'test_site', name='test_site'),
    (r'^gissmo/chaining/', include('smart_selects.urls')),
    (r'^gissmo/', include(admin.site.urls))
)

urlpatterns += patterns(
    '',
    (
        r'^media/(?P<path>.*)$',
        'django.views.static.serve',
        {
            'document_root': settings.MEDIA_ROOT,
            'show_indexes': True
        }
    ),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
