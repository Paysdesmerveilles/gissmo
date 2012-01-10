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
    (r'^report_equip/$', 'report_equip'),
    (r'^report_station/$', 'report_station'),    
    (r'^site_maps/$', 'site_maps'),
)

