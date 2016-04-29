from django.contrib import admin

from equipment.models import (
    Configuration,
    Equipment,
    ForbiddenEquipmentModel,
    IPAddress,
    Model,
    Parameter,
    Service,
    Type,
    Value,
)


class TypeAdmin(admin.ModelAdmin):
    fields = ['parent', 'name', 'rank']
    list_display = ('name', 'parent')
    list_filter = ['parent']
    search_fields = ['name', 'parent__name']
    ordering = ['name']


class ValueInline(admin.TabularInline):
    model = Value
    extra = 2


class ParameterAdmin(admin.ModelAdmin):
    fields = ['name', 'model']
    list_display = ('model', 'name')
    search_fields = ['name', 'model__name']

    inlines = [ValueInline]


class ModelAdmin(admin.ModelAdmin):
    fields = ['name', '_type', 'rank', 'manufacturer']
    list_display = ('name', '_type')
    list_filter = ['_type']
    search_fields = ['name']
    ordering = ['name']


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 2


class IPAddressInline(admin.TabularInline):
    model = IPAddress
    extra = 1


class ConfigurationInline(admin.TabularInline):
    # TODO: Create a form with a selectable field that contains only
    # params/value from the linked model
    model = Configuration
    extra = 4
    fields = ['parameter', 'value']


class EquipmentAdmin(admin.ModelAdmin):
    fields = ['name', 'model', 'owner']
    list_display = ('model', 'name', 'owner', 'place', 'state')
    search_fields = ['name', 'model__name', 'owner__name']
    list_filter = ['state']
    ordering = ['model__name']
    # TODO: Disallow to use a model that have no parent

    inlines = [IPAddressInline, ServiceInline, ConfigurationInline]


class ForbiddenEquipmentModelAdmin(admin.ModelAdmin):
    fields = ['original', 'recommended']
    list_display = ('original', 'recommended')
    search_fields = ['original__name', 'recommended__name']


admin.site.register(Type, TypeAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(Model, ModelAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(ForbiddenEquipmentModel, ForbiddenEquipmentModelAdmin)
