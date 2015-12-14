from django.conf.urls import include, url
from django.contrib import admin

from intervention import views as iviews

admin.site.site_header = 'The best sandbox area you ever seen!'

urlpatterns = [
    # Examples:
    # url(r'^$', 'mytest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^lookup_transitions/$',
        iviews.lookup_transitions,
        name='lookup_transitions'),
]
