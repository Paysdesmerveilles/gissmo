from django.conf.urls.defaults import *

urlpatterns = patterns('bdmateriel.views',
    # Example:
    # (r'^monsitedev/', include('monsitedev.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    ####(r'^stationequip/$', 'stationequip'),
    ####(r'^histoequip/$', 'histoequip'),
    ####(r'^histostation/$', 'histostation'),
    url(r'^xhr_station$','xhr_station', name='xhr_station'),
    url(r'^xhr_station_state$','xhr_station_state', name='xhr_station_state'),
    url(r'^xhr_equipment$','xhr_equipment', name='xhr_equipment'),
    url(r'^xhr_equip_state$', 'xhr_equip_state', name='xhr_equip_state'),
    url(r'^site_maps/$', 'site_maps', name='site_maps'),
    url(r'^itineraire_maps/$', 'itineraire_maps', name='itineraire_maps'),
    url(r'^get_file/(?P<app_label>.+)/(?P<model_name>.+)/(?P<field_name>.+)/(?P<identifier>\d+)$', 'get_file', name='get_file'),
)

