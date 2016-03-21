from django.contrib import admin

from grid.models import Station

class StationAdmin(admin.ModelAdmin):
    fields = ['code']
    list_display = ('code', 'state')
    list_filter = ('state',)
    search_fields = ['code']

admin.site.register(Station, StationAdmin)
