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
    url(r'^report_equip/$', 'report_equip', name='report_equip'),
    url(r'^report_station/$', 'report_station', name='report_station'),    
    url(r'^site_maps/$', 'site_maps', name='site_maps'),
    url(r'^get_file/(?P<app_label>.+)/(?P<model_name>.+)/(?P<field_name>.+)/(?P<identifier>\d+)$', 'get_file', name='get_file'),
)

