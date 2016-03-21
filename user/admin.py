from django.contrib import admin

from user.models import Organism


class OrganismAdmin(admin.ModelAdmin):
    list_display = ['name', '_type', 'parent']
    list_filter = ['_type']
    search_fields = ['name']


admin.site.register(Organism, OrganismAdmin)
