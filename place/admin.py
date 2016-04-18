from django.contrib import admin

from place.models import (
    Place,
    PlaceDocument)


class PlaceDocumentInline(admin.TabularInline):
    model = PlaceDocument
    extra = 1


class PlaceAdmin(admin.ModelAdmin):
    fields = ['name', '_type', 'operator', 'parent']
    list_display = ('name', '_type', 'operator', 'parent')
    list_filter = ['_type']
    search_fields = ['name', 'operator', 'parent']

    inlines = (PlaceDocumentInline,)


admin.site.register(Place, PlaceAdmin)
