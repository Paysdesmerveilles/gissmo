from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic.base import RedirectView

from gissmo import __version__ as gissmo_version

from intervention import views as iviews

# Admin configuration
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
    url(r'^api/v2/', include('api.urls'), name='api'),
    url(r'^api/$', RedirectView.as_view(url='v2', permanent=False), name='api_redirect'),
    url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
