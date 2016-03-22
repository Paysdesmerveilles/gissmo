from django import forms
from django.contrib import admin
from django.contrib.admin import widgets

from grid.models import (
    Channel,
    Installation,
    Network,
    Station,
)


class NetworkAdmin(admin.ModelAdmin):
    fields = ['code', 'name', 'start', 'end', 'description']
    list_display = ['code', 'name', 'start', 'end']
    search_fields = ['code', 'name', 'start', 'end']


class InstallationForm(forms.ModelForm):
    start = forms.DateTimeField(widget=widgets.AdminSplitDateTime())

    class Meta:
        model = Installation
        fields = [
            'parent',
            'equipment',
            'built',
            '_type',
            'depth',
            'start',
            'end']


class InstallationAdmin(admin.ModelAdmin):
    # We add a Form just because of 'start' non-editable field
    # Cf. https://code.djangoproject.com/ticket/26238
    form = InstallationForm
    list_display = ('equipment', 'built', '_type', 'start', 'end')
    list_filter = ['_type']
    search_fields = ['equipment__name', 'start', 'end']

    # TODO: Add configurations as Inline using a throug= table
    # TODO: Filtering configurations per equipment


class ChannelAdmin(admin.ModelAdmin):
    # TODO: Display start date for installation field
    # TODO: Make installation field as a "AutoComplete" field
    fields = [
        'network',
        'installation',
        'code',
        'sample_rate',
        'azimuth',
        'dip',
        'start',
        'end']
    list_display = ('code', 'network', 'sample_rate', 'start', 'end')
    list_filter = ['network__code', 'code']


class StationAdmin(admin.ModelAdmin):
    fields = ['code']
    list_display = ('code', 'state')
    list_filter = ('state',)
    search_fields = ['code']


admin.site.register(Network, NetworkAdmin)
admin.site.register(Installation, InstallationAdmin)
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Station, StationAdmin)
