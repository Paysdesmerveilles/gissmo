from django.contrib import admin

from affiliation.models import Organism


class OrganismAdmin(admin.ModelAdmin):
    list_display = ['name', '_type', 'parent']
    list_filter = ['_type']
    search_fields = ['name']
    filter_horizontal = ('users',)


admin.site.register(Organism, OrganismAdmin)
