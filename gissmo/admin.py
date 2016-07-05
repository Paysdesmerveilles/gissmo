# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms
from django.contrib import (
    admin,
    messages,
)
from django.contrib.admin import SimpleListFilter
from django.contrib.admin.widgets import (
    AdminDateWidget,
    AdminSplitDateTime,
    AdminTimeWidget,
    AdminURLFieldWidget,
)
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.forms import Textarea
from django.shortcuts import (
    HttpResponseRedirect,
    get_object_or_404,
    redirect,
)
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.forms.formsets import formset_factory

from gissmo.models import *  # NOQA
from gissmo.forms import *  # NOQA
from gissmo.views import *  # NOQA
from gissmo.helpers import format_date
from gissmo.validators import validate_equip_model


class URLFieldWidget(AdminURLFieldWidget):

    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<input type="button" '
                         u'value="View Link" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value)" />' % (widget, attrs['id']))


class LabeledHiddenInput(forms.HiddenInput):

    def render(self, name, value, attrs=None):
        status = self.choices.queryset.get(pk=value)
        h_input = super(LabeledHiddenInput, self).render(
            name, value, attrs=None)
        return mark_safe("%s %s" % (status, h_input))


class EquipModelDocInline(admin.TabularInline):
    model = EquipModelDoc
    fields = ('document_type', 'document_title', 'begin_effective',
              'end_effective', 'document_equip_model', 'private_link')
    form = EquipModelDocInlineForm
    exclude = ['owner']
    extra = 0
    ordering = ['-begin_effective', ]

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }


class ParameterEquipInline(admin.TabularInline):
    model = ParameterEquip
    extra = 0


"""
Custom filter for the equipment model change list
"""


class EquipModelFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Supertype or Type'

    # Parameter for the filter that will be used in the URL query.
    # I use cf as the parameter_name for the custom filter
    parameter_name = 'cf'

    template = "model_filter2.html"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        Liste = []
        Equip_Supertype = EquipSupertype.objects.all().order_by(
            'equip_supertype_name')

        """
        Tree presentation of the filter choice.
        Indentation by space character unichr(160) and to distinguish
        the equipment type we enclose it by <>
        and equipment model by []
        """
        for equip_supertype in Equip_Supertype:
            Liste.append(('Stype_' + str(equip_supertype.id),
                          equip_supertype.equip_supertype_name))
            Equip_Type = EquipType.objects.filter(
                equip_supertype=equip_supertype).order_by('equip_type_name')
            for equip_type in Equip_Type:
                Liste.append(('Type__' + str(equip_type.id),
                              equip_type.equip_type_name))
        return Liste

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            if self.value()[:5] == 'Stype':
                return queryset.filter(
                    equip_type__equip_supertype__id__exact=self.value()[6:])
            if self.value()[:5] == 'Type_':
                return queryset.filter(
                    equip_type__id__exact=self.value()[6:])


class EquipModelAdmin(admin.ModelAdmin):
    list_display = [
        'equip_supertype',
        'equip_type',
        'equip_model_name',
        'have_a_manufacturer']
    list_display_links = ['equip_model_name']
    list_filter = [EquipModelFilter]
    ordering = [
        'equip_type__equip_supertype',
        'equip_type',
        'equip_model_name']
    search_fields = ['equip_model_name']
    form = EquipModelForm

    fieldsets = [('', {'fields': [
                  (
                      'equip_type',
                      'equip_model_name',
                      'manufacturer',
                      'is_network_model')]})]

    inlines = [EquipModelDocInline, ParameterEquipInline]

    def save_formset(self, request, form, formset, change):
        """Reference du code
            http://stackoverflow.com/questions/3016158/\
django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field
        """
        instances = formset.save(commit=False)
        # New in Django 1.7: (formset with commit=False are no longer deleted)
        # https://docs.djangoproject.com/en/1.8/releases/1.7/#miscellaneous
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # Check if it is the correct type of inline
            if isinstance(instance, EquipModelDoc):
                instance.equip_type = form.cleaned_data['equip_type']
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()


class EquipDocInline(admin.TabularInline):
    model = EquipDoc
    fields = ('document_type', 'document_title', 'begin_effective',
              'end_effective', 'document_equip', 'private_link')
    form = EquipDocInlineForm
    exclude = ['owner']
    extra = 0
    ordering = ['-begin_effective']

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 3


class IPAddressInline(admin.TabularInline):
    model = IPAddress
    form = IPAddressInlineForm
    extra = 1


class ConfigEquipInline(admin.TabularInline):
    model = ConfigEquip
    extra = 0
    formset = ConfigEquipInlineFormset


class EquipFilter(SimpleListFilter):
    """
    Custom filter for the equipment change list
    """
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Supertype, Type or Model'

    # Parameter for the filter that will be used in the URL query.
    # I use cf as the parameter_name for the custom filter
    parameter_name = 'cf'

    template = "equip_filter.html"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        liste = []
        Equip_Supertype = EquipSupertype.objects.all().order_by(
            'equip_supertype_name')

        """
       Tree presentation of the filter choice.
       Indentation by space character unichr(160) and to distinguish
       the equipment type we enclose it by <>
       and equipment model by []
       """
        for equip_supertype in Equip_Supertype:
            liste.append(('Stype_' + str(equip_supertype.id),
                          equip_supertype.equip_supertype_name))
            Equip_Type = EquipType.objects.filter(
                equip_supertype=equip_supertype).order_by('equip_type_name')
            for equip_type in Equip_Type:
                liste.append(('Type__' + str(equip_type.id),
                              equip_type.equip_type_name))
                Equip_Model = EquipModel.objects.filter(
                    equip_type=equip_type).order_by('equip_model_name')
                for equip_model in Equip_Model:
                    liste.append(('Model_' + str(equip_model.id),
                                  equip_model.equip_model_name))
        return liste

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            if self.value()[:5] == 'Stype':
                return queryset.filter(
                    equip_model__equip_type__equip_supertype__id=self.value()[6:])  # NOQA
            if self.value()[:5] == 'Type_':
                return queryset.filter(
                    equip_model__equip_type__id=self.value()[6:])
            if self.value()[:5] == 'Model':
                return queryset.filter(
                    equip_model__id__exact=self.value()[6:])


class OwnerFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Owner'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'owner'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        lookup_list = Organism.objects.filter(
            Q(_type=Organism.OBSERVATORY) |
            Q(_type=Organism.NETWORK) |
            Q(_type=Organism.UNKNOWN)).values_list(
                'id',
                'name').distinct()
        return lookup_list

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or 'other')
        # to decide how to filter the queryset.
        if self.value():
            return queryset.filter(owner=self.value())
        else:
            return queryset


class EquipmentAdmin(admin.ModelAdmin):
    list_display = [
        'equip_supertype',
        'equip_type',
        'equip_model',
        'serial_number',
        'last_state',
        'last_station',
        'owner']
    list_display_links = ['serial_number']
    list_filter = [EquipFilter, 'last_state', 'last_station']
    ordering = [
        'equip_model__equip_type__equip_supertype',
        'equip_model__equip_type',
        'equip_model',
        'serial_number']
    search_fields = [
        'equip_model__equip_model_name',
        'serial_number']
    form = EquipmentForm

    fieldsets = [
        ('Equipements', {
            'fields': [
                (
                    'equip_model',
                    'serial_number',
                    'owner',
                    'purchase_date',
                    'stockage_site')]}),
        ('Contacts', {
            'fields': [
                (
                    'vendor',
                    'contact')],
            'classes': ['collapse']}),
        ('Other information', {
            'fields': [('note')],
            'classes': ['collapse']})]

    inlines = [EquipDocInline, ConfigEquipInline]

    class Media:
        js = ["js/my_ajax_function.js"]

    def changemodel_formset(self, equipment):
        """
        Formset factory that will create an Equipment change model form
        with a list of Equipment's model that are compatible with the choosen
        model.
        """
        class EquipmentChangeModelForm(forms.Form):
            """
            Forms that permit to give the new Equipment's Model for
            a given Equipment.
            Filtering regarding given equipment type.
            """
            equip_model = forms.ModelChoiceField(
                queryset=EquipModel.objects.filter(
                    equip_type=equipment.equip_model.equip_type),
                label='New model',
                validators=[validate_equip_model])

        return formset_factory(form=EquipmentChangeModelForm, )

    def get_urls(self):
        """
        Add new 'changemodel' possibility
        """
        urls = super(EquipmentAdmin, self).get_urls()
        my_urls = [
            url(
                r'^(.+)/changemodel/$',
                self.changemodel_view_step1,
                name='changemodel_step1'),
            url(
                r'^(.+)/changemodel/(.+)$',
                self.changemodel_view_step2,
                name='changemodel_step2'),
        ]
        return my_urls + urls

    def changemodel_view_step1(self, request, equipment_id):
        """
        Display changemodel view that permits to change equipment's model for
        a given Equipment ID.
        """
        # Default values
        equips = Equipment.objects.filter(id=equipment_id).prefetch_related(
            'chain_set__chainconfig_set__value__parameter',
            'chain_set__chainconfig_set__channel__channel_code',
            'chain_set__chainconfig_set__channel__network',
            'chain_set__chainconfig_set__channel__station',)
        equipment = equips[0]
        title = "Change equipment's model for: %(model)s (%(serial)s)" % {
            'model': equipment.equip_model,
            'serial': equipment.serial_number}
        context = dict(
            self.admin_site.each_context(request),
            title=title,
            equipment=equipment,
        )
        if request.method == 'POST':
            # Deal with errors by instanciating the formset then fill in with
            # given request.POST data
            EquipmentFormSet = self.changemodel_formset(equipment)
            formset = EquipmentFormSet(request.POST)
            # If errors, show them
            if not formset.is_valid():
                context.update({'form': formset})
            else:
                # TODO: manage case where equipment model is emtpy with a
                # specific view
                for form in formset.cleaned_data:
                    model = form.get('equip_model', None)
                return redirect(reverse('admin:changemodel_step2', args=(equipment_id, model.id)))
        else:
            form = self.changemodel_formset(equipment)
            context.update({'form': form})

        return render(request, "changemodel_step1.html", context)

    def changemodel_view_step2(self, request, equipment_id, model_id):
        equips = Equipment.objects.filter(id=equipment_id).prefetch_related(
            'chain_set__chainconfig_set__value__parameter',
            'chain_set__chainconfig_set__parameter',
            'chain_set__chainconfig_set__channel__channel_code',
            'chain_set__chainconfig_set__channel__network',
            'chain_set__chainconfig_set__channel__station',)
        equipment = equips[0]
        model = EquipModel.objects.get(pk=model_id)
        title = "Simulation from: %(model)s (%(serial)s), to: %(new_model)s" % {
            'model': equipment.equip_model,
            'serial': equipment.serial_number,
            'new_model': model}
        context = dict(
            self.admin_site.each_context(request),
            title=title,
        )
        modifications = changemodel_simulation(equipment, model)
        elements, message = changemodel_display(modifications, equipment)
        context.update({
            'elements': elements,
            'dynamic_states': [
                'missing',
                'new',
                'conflict',
            ],
            'message': message,
        })

        return render(request, "changemodel_step2.html", context)

    def _get_equipment_inlines_regarding_model(self, equip_model):
        """
        Only display IPAddress and Services Inlines if Equipment's Model
        contains 'Contains network configuration' set to True.
        """
        res = self.inlines
        inlines = [IPAddressInline, ServiceInline]
        if equip_model.is_network_model is True:
            [res.append(x) for x in inlines if x not in res]
        else:
            [res.remove(x) for x in inlines if x in res]
        return res

    def get_formsets_with_inlines(self, request, obj=None, **kwargs):
        """
        Change inlines regarding model content.
        """
        res = super(EquipmentAdmin, self).get_formsets_with_inlines(
            request, obj, **kwargs)
        if obj and obj.equip_model:
            self.inlines = self._get_equipment_inlines_regarding_model(
                obj.equip_model)
        return res

    def get_queryset(self, request):
        """
        Show only equipment according to the user's group (project)
        """
        qs = super(EquipmentAdmin, self).get_queryset(
            request).prefetch_related(
            'last_station')
        groups = request.user.groups.all()

        allowed_sites = []
        for g in groups:
            allowed_sites += g.project.get_sites_ids()
        return qs.filter(
            last_station_id__in=allowed_sites).prefetch_related(
                'last_station')

    def save_model(self, request, obj, form, change):
        """
        Gives stockage_site and purchase_date to Equipment so that it can
        generate interventions such as buying equipment and make Equipment in
        'to test' status.
        """
        obj.stockage_site = form.cleaned_data['stockage_site']
        obj.actor = request.user.username
        super(EquipmentAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Reference du code
        http://stackoverflow.com/questions/3016158/\
django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field
        """
        instances = formset.save(commit=False)
        # New in Django 1.7: (formset with commit=False are no longer deleted)
        # https://docs.djangoproject.com/en/1.8/releases/1.7/#miscellaneous
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # Check if it's the correct type of inline
            if isinstance(instance, EquipDoc):
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()


class ForbiddenEquipmentModelAdmin(admin.ModelAdmin):
    list_display = [
        'original',
        'recommended']
    ordering = ['original']
    search_fields = ['original', 'recommended']
    form = ForbiddenEquipmentModelForm


####
#
# StationAdmin's section
#
####


class BuiltInline(admin.TabularInline):
    model = Built
    extra = 0
    classes = ['collapse', 'collapsed']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1})},
    }


class StationDocInline(admin.TabularInline):
    model = StationDoc
    fields = ('document_type', 'document_title', 'begin_effective',
              'end_effective', 'document_station', 'private_link')
    form = StationDocInlineForm
    exclude = ['owner', ]
    extra = 0
    ordering = ['-begin_effective', ]

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

"""
Custom filter for the stationsite change list
"""


class StationSiteFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'Operator'

    # Parameter for the filter that will be used in the URL query.
    # I use cf as the parameter_name for the custom filter
    parameter_name = 'operator'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        Liste = []
        Operator_station = StationSite.objects.values_list(
            'operator', flat=True)
        liste_val_distinct_triee = list(sorted(set(Operator_station)))

        Operator = Organism.objects.filter(
            id__in=liste_val_distinct_triee).order_by('name')

        """
       Tree presentation of the filter choice.
       """
        for operator in Operator:
            Liste.append(((str(operator.id)), operator.name))
        return Liste

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(operator__id__exact=self.value())


class StationSiteAdmin(admin.ModelAdmin):
    list_display = (
        'station_code',
        'site_name',
        'operator',
        'last_state',
        'site_type',
        'latitude',
        'longitude')
    list_filter = [StationSiteFilter, 'site_type']
    ordering = ['station_code']
    search_fields = ['station_code', 'site_name', 'operator__name']
    readonly_fields = ['googlemap_link']
    form = StationSiteForm

    fieldsets = [
        ('Main information', {
            'fields': [
                ('site_type',
                    'station_code',
                    'site_name',
                    'station_parent',
                    'operator',
                    'creation_date',
                    'project'),
                ('latitude', 'longitude', 'elevation', 'googlemap_link'),
                ('ground_type')]}),
        ('Contacts', {
            'fields': [('contact')],
            'classes': ['collapse']}),
        ('Address', {
            'fields': [
                ('site_description'),
                ('address', 'zip_code', 'town'),
                ('county', 'region', 'country')],
            'classes': ['collapse']}),
        ('Other information', {
            'fields': [
                ('note'),
                ('private_link'),
                ('geology'),
                ('station_description'),
                ('alternate_code', 'historical_code', 'restricted_status'),
            ],
            'classes': ['collapse']}),
    ]

    inlines = [BuiltInline, StationDocInline, ]

    class Media:
        js = ["js/spread_date.js", "js/sample_rate.js"]

    def googlemap_link(self, obj):
        res = ''
        if obj.id:
            latitude = obj.latitude
            longitude = obj.longitude
            if longitude and latitude:
                url = "https://www.google.com/maps/place/%s,%s/@%s,%s,17z/data=!3m1!1e3" % (
                    latitude,
                    longitude,
                    latitude,
                    longitude)
                res = mark_safe(
                    '<a href="%s" target="_blank">Google Map View</a>' % url)
        return res

    googlemap_link.short_description = 'Localization'

    def get_form(self, request, obj=None, **kwargs):
        form = super(StationSiteAdmin, self).get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form

    # Redefine queryset to show only site according to the user's group
    def get_queryset(self, request):
        qs = super(StationSiteAdmin, self).get_queryset(request)
        groups = request.user.groups.all()

        allowed_sites = []
        for g in groups:
            allowed_sites += g.project.get_sites_ids()
        return qs.filter(id__in=allowed_sites)

    def save_model(self, request, obj, form, change):
        """
        Overide save_model to generate intervention and intervstation object
        Create station code as action and in construction for the status
        """
        obj.project = form.cleaned_data['project']
        obj.actor = request.user.username
        obj.save()
        super(StationSiteAdmin, self).save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """
        Réference du code
        http://stackoverflow.com/questions/3016158/\
django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field
        """
        instances = formset.save(commit=False)
        # New in Django 1.7: (formset with commit=False are no longer deleted)
        # https://docs.djangoproject.com/en/1.8/releases/1.7/#miscellaneous
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # Check if it is the correct type of inline
            if isinstance(instance, StationDoc):
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

    def get_urls(self):
        """
        Add new possibilities:
            - closechannels
            - createchannels
        """
        urls = super(StationSiteAdmin, self).get_urls()
        my_urls = [
            url(
                r'^(.+)/closechannels/$',
                self.closechannels_view,
                name='closechannels'),
            url(
                r'^(.+)/createchannels/$',
                self.createchannels_view,
                name='createchannels'),
        ]
        return my_urls + urls

    def closechannels_formset(self, station):
        class StationSiteClosechannelsForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super(
                    StationSiteClosechannelsForm,
                    self).__init__(*args, **kwargs)
                for channel in station.channel_set.filter(
                    end_date=None).prefetch_related(
                        'network',
                        'channel_code'):
                    name = "%s : %s : %s : %s (freq. %s) Date" % (
                        station.station_code,
                        channel.network.network_code,
                        channel.location_code,
                        channel.channel_code.channel_code,
                        channel.sample_rate)
                    self.fields[
                        '%s' % channel.id] = forms.SplitDateTimeField(
                            label=name,
                            widget=AdminSplitDateTime,
                            required=False)

        return formset_factory(form=StationSiteClosechannelsForm, )

    def closechannels_view(self, request, station_id):
        """
        Work with channels linked to a station to close them.
        """
        station = StationSite.objects.filter(id=station_id).prefetch_related(
            'channel_set__channel_code',
            'channel_set__network').first()
        title = "Close opened channels for %(station)s station" % {
            'station': station.station_code}
        # media add javascript links into result (if included in template)
        date_widget_media = AdminDateWidget().media
        time_widget_media = AdminTimeWidget().media
        context = dict(
            self.admin_site.each_context(request),
            title=title,
            station=station,
            media=self.media + time_widget_media + date_widget_media,
        )
        if request.method == 'POST':
            StationFormSet = self.closechannels_formset(station)
            formset = StationFormSet(request.POST)
            context.update({'form': formset})
            if formset.is_valid():
                for form in formset.cleaned_data:
                    return closechannels_process(
                        request, form, station_id, context)
        else:
            form = self.closechannels_formset(station)
            context.update({'form': form})

        return render(request, "closechannels_view.html", context)

    def createchannels_formset(self, station):
        class CreateChannelChainForm(forms.Form):
            equipments = [(x.id, x) for x in station.equipment_set.all()]
            equipment = forms.ChoiceField(
                choices=[('', '--')] + equipments,
                label='Equipment',
                required=True,
                initial='')
            order = forms.ChoiceField(
                choices=[('', '--')] + list(Chain.ORDER_CHOICES),
                label='Type',
                required=True,
                initial='')
        return formset_factory(form=CreateChannelChainForm, extra=3)

    def createchannels_view(self, request, station_id, code=None):
        """
        Aims to be a channel creator wizard. Always create 3 channels.
        """
        station = StationSite.objects.filter(id=station_id).first()
        title = "Create 3 channels for %(station)s station" % {
            'station': station.station_code}
        # media add javascript links into result (if included in template)
        date_widget_media = AdminDateWidget().media
        time_widget_media = AdminTimeWidget().media
        context = dict(
            self.admin_site.each_context(request),
            title=title,
            station=station,
            media=self.media + time_widget_media + date_widget_media,
        )
        if request.method == 'POST':
            form = CreateChannelForm(request.POST)
            CreateChannelChainFormSet = self.createchannels_formset(station)
            chain_formset = CreateChannelChainFormSet(request.POST)
            context.update({'form': form, 'chain_form': chain_formset})
            if form.is_valid():
                return createchannels_process(
                    request, form, chain_formset, station_id, context)
        else:
            form = CreateChannelForm()
            CreateChannelChainFormSet = self.createchannels_formset(station)
            chain_formset = CreateChannelChainFormSet()
            context.update({'form': form, 'chain_form': chain_formset})

        return render(request, "createchannels_view.html", context)


####
#
# Table code Admin's section
#
####


class EquipTypeAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type_name']
    list_filter = ['equip_supertype']


class IntervStationInline(admin.TabularInline):
    model = IntervStation
    extra = 0
    max_num = 1
    formset = IntervStationInlineFormset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1})},
    }


class IntervEquipInline(admin.TabularInline):
    model = IntervEquip
    extra = 0
    form = IntervEquipInlineForm
    formset = IntervEquipInlineFormset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1})},
    }


class IntervDocInline(admin.TabularInline):
    model = IntervDoc
    extra = 1
    fields = ('_file', 'description')
    form = IntervDocInlineForm


class CustomIntervUserInline(admin.TabularInline):
    form = IntervUserInlineForm
    formset = IntervUserInlineFormset


class IntervUserInline(CustomIntervUserInline):
    model = IntervUser
    extra = 0
    fields = ('user', 'note')


class IntervOrganismInline(admin.TabularInline):
    model = IntervOrganism
    extra = 0
    fields = ('organism', 'note')


class InterventionAdmin(admin.ModelAdmin):
    list_display = ['station', 'format_date']
    list_filter = ['station', ]
    ordering = ['-intervention_date', 'station']
    search_fields = ['station__station_code', 'intervention_date', ]
    form = InterventionForm

    inlines = [
        IntervUserInline,
        IntervOrganismInline,
        IntervStationInline,
        IntervEquipInline,
        IntervDocInline]

    class Media:
        js = ["js/my_ajax_function.js"]

    # Redefine queryset to show only intervention according to the user's
    # group
    def get_queryset(self, request):
        qs = super(InterventionAdmin, self).get_queryset(request)
        groups = request.user.groups.all()

        allowed_sites = []
        for g in groups:
            allowed_sites += g.project.get_sites_ids()
        return qs.filter(station_id__in=allowed_sites)

    def response_change(self, request, obj):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, 'Element successfully modified')
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_stationsite_change" % (content_type.app_label),
                args=(obj.station.id,)))
        else:
            return super(InterventionAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, 'Element successfully added')
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_stationsite_change" % (content_type.app_label),
                args=(obj.station.id,)))
        else:
            return super(InterventionAdmin, self).response_add(
                request,
                obj,
                post_url_continue)

    def format_date(self, obj):
        return format_date(obj.intervention_date)

    format_date.short_description = 'Date (yyyy-mm-dd HH24:MM)'
    format_date.admin_order_field = 'intervention_date'

    def _create_formsets(self, request, obj, change):
        """
        override to provide initial data for inline formset.
        Especially current user for IntervUserInline.
        And current equipment (if present in URL) for IntervEquipInline.
        """
        formsets = []
        inline_instances = []
        prefixes = {}
        get_formsets_args = [request]
        if change:
            get_formsets_args.append(obj)
        for FormSet, inline in self.get_formsets_with_inlines(*get_formsets_args):
            prefix = FormSet.get_default_prefix()
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            if prefixes[prefix] != 1 or not prefix:
                prefix = "%s-%s" % (prefix, prefixes[prefix])
            formset_params = {
                'instance': obj,
                'prefix': prefix,
                'queryset': inline.get_queryset(request),
            }
            if request.method == 'POST':
                formset_params.update({
                    'data': request.POST,
                    'files': request.FILES,
                    'save_as_new': '_saveasnew' in request.POST
                })

            if change:
                formsets.append(FormSet(**formset_params))
                inline_instances.append(inline)
            else:
                # get equip
                equip_id = request.GET.get('equip', None)
                inline_initial_data = None
                if isinstance(inline, IntervUserInline):
                    inline_initial_data = [
                        {'user': request.user},
                    ]
                elif isinstance(inline, IntervEquipInline) and equip_id:
                    inline_initial_data = [
                        {'equip': Equipment.objects.get(pk=equip_id)},
                    ]
                if inline_initial_data:
                    formset_params['initial'] = inline_initial_data
                formsets.append(FormSet(**formset_params))
                inline_instances.append(inline)

        return formsets, inline_instances


class ChainInline(admin.TabularInline):
    model = Chain
    extra = 0
    formset = ChainInlineFormset

    readonly_fields = ['configuration', 'delete']

    def __init__(self, *args, **kwargs):
        super(ChainInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    def configuration(self, obj):
        if obj.id:
            # Hack to obtain the channel ID to be able to pass it to the
            # config link as parameter
            channel = get_object_or_404(Chain, pk=obj.id).channel.id
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            url = reverse(
                'admin:%s_chain_change' % (content_type.app_label),
                args=[obj.id]) + '?channel=' + str(channel)
            return mark_safe("<a href='%s'>config</a>" % url)

    def delete(self, obj):
        if obj.id:
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            url = reverse(
                'admin:%s_chain_change' % (content_type.app_label),
                args=[obj.id]) + 'delete/'
            return mark_safe("<a href='%s'>delete</a>" % url)

    def get_formset(self, request, obj=None, **kwargs):
        """
        Put request in formset so that we can fetch station ID if needed.
        For an example to filter Equipments regarding station_id
        """
        formset = super(ChainInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def get_queryset(self, request):
        qs = super(ChainInline, self).get_queryset(request)
        return qs.prefetch_related('equip__equip_model')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1})},
    }


class ChainConfigInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
    formset = ChainConfigInlineFormset

    fields = ('parameter', 'value')

    def get_queryset(self, request):
        qs = super(ChainConfigInline, self).get_queryset(request)
        return qs.prefetch_related('parameter__equip_model')


class ChannelChainInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
    max_num = 0

    # To improve a little bit performance, we only display param/value
    # as readonly fields to let user insert new param/value by using
    # "config" link in ChainConfigInline
    fields = ['parameter', 'value']
    readonly_fields = ('parameter', 'value')

    def formfield_for_dbfield(self, db_field, **kwargs):
        # On suppose que le modèle a un champ image
        if db_field.name == 'chain':
            kwargs['widget'] = forms.TextInput(
                attrs={'style': 'width: 1px'})
            kwargs.pop('request', None)  # erreur sinon
            return db_field.formfield(**kwargs)
        return super(ChannelChainInline, self).formfield_for_dbfield(
            db_field,
            **kwargs)

    def get_queryset(self, request):
        qs = super(ChannelChainInline, self).get_queryset(request)
        return qs.prefetch_related(
            'chain__equip__equip_model',
            'parameter__equip_model',
            'value')


class ChannelAdmin(admin.ModelAdmin):
    model = Channel
    save_as = True
    form = ChannelForm

    # list_display = [
    #     'network',
    # 'station',
    # 'channel_code',
    # 'location_code',
    # 'start_date',
    # 'end_date']
    # list_editable = ['end_date' ]

    actions = ['delete_selected']

    fieldsets = [
        ('', {
            'fields': [
                ('network',
                    'station',
                    'channel_code',
                    'location_code'),
                ('latitude',
                    'longitude',
                    'elevation',
                    'depth',
                    'azimuth',
                    'dip'),
                ('sample_rate', 'accept_anyway', 'start_date', 'end_date')]}),
        ('Data types', {
            'fields': [('data_type')],
            'classes': ['collapse']}),
        ('Other information', {
            'fields': [
                ('description'),
                ('alternate_code', 'historical_code', 'restricted_status'),
                ('storage_format', 'clock_drift', 'calibration_units')],
            'classes': ['collapse']})]

    search_fields = [
        'network__network_code',
        'station__station_code',
        'channel_code__channel_code']
    inlines = [ChainInline, ChannelChainInline]

    class Media:
        js = ["js/my_ajax_function.js"]

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        gmp = super(ChannelAdmin, self).get_model_perms(request)
        if request.user.is_superuser:
            return gmp
        else:
            return {}

# TODO: a lot of todo
# blinder la generation automatique de parametre de config selon modele equip
# empecher tout changement
# generer l'ordre automatiquement

    def save_formset(self, request, form, formset, change):
        """
        Réference du code
        http://stackoverflow.com/questions/3016158/\
django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field
        """
        instances = formset.save(commit=False)
        # New in Django 1.7: (formset with commit=False are no longer deleted)
        # https://docs.djangoproject.com/en/1.8/releases/1.7/#miscellaneous
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # Check if it's the correct type of inline
            if isinstance(instance, Chain):
                instance.save()
                # Use given chain to deploy its parameters (Inline Config.)
                if '_saveasnew' not in request.POST:
                    instance.set_chainconfig_parameters()
            elif isinstance(instance, ChainConfig):
                old_chain = get_object_or_404(Chain, pk=instance.chain.id)
                new_chain = Chain.objects.filter(
                    channel=instance.channel.id,
                    order=old_chain.order,
                    equip=old_chain.equip)
                if new_chain:
                    instance.chain = new_chain[0]
                instance.save()
            else:
                formset.save()

    def response_change(self, request, obj):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        msg = 'Element successfully modified'
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, msg)
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_stationsite_change" % (content_type.app_label),
                args=(obj.station.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success(request, msg)
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChannelAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        msg = 'Element successfully added'
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, msg)
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_stationsite_change" % (content_type.app_label),
                args=(obj.station.id,)))
        else:
            # This makes the response go to the newly created model's change
            # page without using reverse
            if '_saveasnew' in request.POST:
                messages.success(request, msg)
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChannelAdmin, self).response_add(
                    request,
                    obj,
                    post_url_continue)

    def get_queryset(self, request):
        qs = super(ChannelAdmin, self).get_queryset(request)
        return qs.prefetch_related(
            'channel_code',
            'network',
            'station')


class ChainAdmin(admin.ModelAdmin):
    model = Chain

    readonly_fields = ['channel', 'order', 'equip']

    inlines = [ChainConfigInline, ]

    class Media:
        js = ["js/my_ajax_function.js"]

    # This put the channel into the ChainConfig instance according with the
    # channel value pass through the URL
    def save_formset(self, request, form, formset, change):
        """
        Réference du code
        http://stackoverflow.com/questions/3016158/\
django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field
        """
        instances = formset.save(commit=False)
        # New in Django 1.7: (formset with commit=False are no longer deleted)
        # https://docs.djangoproject.com/en/1.8/releases/1.7/#miscellaneous
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            # Check if it is the correct type of inline
            if isinstance(instance, ChainConfig):
                if not instance.pk:
                    instance.channel = instance.chain.channel
                instance.save()
            else:
                formset.save()

    def response_change(self, request, obj):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        msg = 'Element successfully modified'
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, msg)
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_channel_change" % (content_type.app_label),
                args=(obj.channel.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success(request, msg)
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChainAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        is_continue = '_continue' in request.POST
        is_saveas = '_saveasnew' in request.POST
        is_add = '_addanother' in request.POST
        msg = "Element successfully added"
        if not is_continue and not is_saveas and not is_add:
            messages.success(request, msg)
            # Trick to get the app label
            content_type = ContentType.objects.get_for_model(obj.__class__)
            return HttpResponseRedirect(reverse(
                "admin:%s_channel_change" % (content_type.app_label),
                args=(obj.channel.id,)))
        else:
            # This makes the response go to the newly created model's change
            # page without using reverse
            if '_saveasnew' in request.POST:
                messages.success(request, msg)
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChainAdmin, self).response_add(
                    request,
                    obj,
                    post_url_continue)

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    def get_queryset(self, request):
        qs = super(ChainAdmin, self).get_queryset(request)
        return qs.prefetch_related('equip__equip_model')


class NetworkAdmin(admin.ModelAdmin):
    model = Network
    ordering = ['network_code']

    fieldsets = [
        ('', {'fields': [('network_code', 'start_date', 'end_date'), ]}),
        ('Other information', {
            'fields': [
                ('description'),
                ('alternate_code', 'historical_code', 'restricted_status')],
            'classes': ['collapse']})]


class ProjectAdmin(BaseGroupAdmin):
    filter_horizontal = ('permissions', 'sites')

    # Redefine queryset to show only group according to the user's project
    def get_queryset(self, request):
        qs = super(ProjectAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(manager_id=request.user.id)

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        gmp = super(ProjectAdmin, self).get_model_perms(request)
        if request.user.is_superuser:
            return gmp
        else:
            is_manager = Project.objects.filter(manager_id=request.user.id)
            if not is_manager:
                return {}
            return gmp

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('name', 'manager')
        return self.readonly_fields


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 0


class ParameterEquipAdmin(admin.ModelAdmin):
    model = ParameterEquip
    search_fields = ['equip_model__equip_model_name', 'parameter_name', ]

    list_display = ['equip_model', 'parameter_name', ]

    inlines = [ParameterValueInline, ]


class ParameterValueAdmin(admin.ModelAdmin):
    model = ParameterValue
    list_filter = ['parameter', ]
    search_fields = ['parameter__equip_model__equip_model_name',
                     'parameter__parameter_name', ]

    list_display = ['parameter', 'value', 'default_value']
    list_editable = ['default_value']


class ChannelCodeAdmin(admin.ModelAdmin):
    model = ChannelCode
    search_fields = ['channel_code', ]

    list_display = ['channel_code', 'presentation_rank', ]


class OrganismAdmin(admin.ModelAdmin):
    model = Organism
    ordering = ['name']
    search_fields = ['name']
    list_filter = ['_type']
    list_display = ['name', '_type', 'parent']
    filter_horizontal = ('users', )

    def delete_model(self, request, obj):
        forbidden_element = 'Unknown'
        if obj.name == forbidden_element:
            storage = messages.get_messages(request)
            storage.used = True
            messages.error(
                request,
                'Delete %s is forbidden!' % forbidden_element)
        else:
            return super(OrganismAdmin, self).delete_model(request, obj)


class GroundTypeAdmin(admin.ModelAdmin):
    model = GroundType
    ordering = ['name']
    search_fields = ['name', 'description']
    list_display = ['name', 'description']

"""
Disabling the action "delete_selected" for all the site
"""
admin.site.disable_action('delete_selected')


admin.site.register(Channel, ChannelAdmin)
admin.site.register(Chain, ChainAdmin)
admin.site.register(EquipModel, EquipModelAdmin)
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(ForbiddenEquipmentModel, ForbiddenEquipmentModelAdmin)
admin.site.register(StationSite, StationSiteAdmin)
admin.site.register(Network, NetworkAdmin)
admin.site.register(BuiltType)
admin.site.register(CalibrationUnit)
admin.site.register(DataType)
admin.site.register(EquipModelDocType)
admin.site.register(EquipDocType)
admin.site.register(StationDocType)
admin.site.register(EquipType)
admin.site.register(Intervention, InterventionAdmin)
admin.site.unregister(Group)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ParameterEquip, ParameterEquipAdmin)
admin.site.register(ParameterValue, ParameterValueAdmin)
admin.site.register(ChannelCode, ChannelCodeAdmin)
admin.site.register(Organism, OrganismAdmin)
admin.site.register(GroundType, GroundTypeAdmin)
