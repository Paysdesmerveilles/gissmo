from django.contrib import admin

from place.models import Site


class SiteAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('name', 'state')
    list_filter = ['state']
    search_fields = ['name']

admin.site.register(Site, SiteAdmin)
