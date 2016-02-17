from __future__ import unicode_literals
from gissmo.urls.common import *  # NOQA

from gissmo.settings import dev

from django.conf.urls import (
    url,
    patterns,
    include)

admin.site.site_header = 'Gissmo 1.5-trunk'

if dev.DEBUG:
    import debug_toolbar
    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )
