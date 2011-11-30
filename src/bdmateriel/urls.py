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
    (r'^rapport_equip/$', 'rapport_equip'),
    (r'^rapport_station/$', 'rapport_station'),    
    (r'^site_maps/$', 'site_maps'),
)

