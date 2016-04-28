from django.contrib import admin

from place.models import (
    GroundType,
    Place,
    PlaceDocument)


class GroundTypeAdmin(admin.ModelAdmin):
    fields = ['name', 'description']
    list_display = ('name', 'description')
    search_fields = ['name', 'description']
    ordering = ['name']


class PlaceDocumentInline(admin.TabularInline):
    model = PlaceDocument
    extra = 1


class PlaceAdmin(admin.ModelAdmin):
    fields = ['name', '_type', 'operator', 'parent', 'latitude', 'longitude', 'elevation', 'description']
    list_display = ('name', '_type', 'operator', 'parent')
    list_filter = ['_type']
    search_fields = ['name', 'operator__name', 'parent__name']

    inlines = (PlaceDocumentInline,)


admin.site.register(Place, PlaceAdmin)
admin.site.register(GroundType, GroundTypeAdmin)
