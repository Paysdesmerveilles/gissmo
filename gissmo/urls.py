from django.conf.urls import include, url
from django.contrib import admin

from gissmo import __version__ as gissmo_version

from intervention import views as iviews

admin.site.site_header = 'Gissmo %s' % gissmo_version
admin.site.site_title = 'Gissmo'

urlpatterns = [
    # Examples:
    # url(r'^$', 'gissmo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^lookup_transitions/$',
        iviews.lookup_transitions,
        name='lookup_transitions'),
]
