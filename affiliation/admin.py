from django.contrib import admin

from affiliation.models import Agency


class AgencyAdmin(admin.ModelAdmin):
    list_display = ['name', '_type', 'parent']
    list_filter = ['_type']
    search_fields = ['name']
    filter_horizontal = ('users',)
    ordering = ['name']


admin.site.register(Agency, AgencyAdmin)
