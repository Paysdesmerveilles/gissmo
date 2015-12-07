from django.conf.urls import include, url
from django.contrib import admin

admin.site.site_header = 'My Test'

urlpatterns = [
    # Examples:
    # url(r'^$', 'mytest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
]
