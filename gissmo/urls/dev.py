from django.conf.urls.defaults import patterns
from django.conf import settings

from gissmo.urls.common import *


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
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
