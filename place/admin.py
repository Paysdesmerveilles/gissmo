from django.contrib import admin

from place.models import (
    Built,
    BuiltType,
    Site)


class SiteAdmin(admin.ModelAdmin):
    fields = ['name', '_type', 'operator']
    list_display = ('name', '_type', 'operator')
    list_filter = ['_type']
    search_fields = ['name', 'operator']


class BuiltTypeAdmin(admin.ModelAdmin):
    fields = ['name']
    list_display = ('name',)
    search_fields = ['name']


class BuiltAdmin(admin.ModelAdmin):
    fields = ['name', '_type', 'site']
    list_display = ('name', '_type', 'site')
    list_filter = ['_type']
    search_fields = ['name', 'site']

admin.site.register(Site, SiteAdmin)
admin.site.register(BuiltType, BuiltTypeAdmin)
admin.site.register(Built, BuiltAdmin)
