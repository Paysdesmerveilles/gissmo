# coding=utf-8

from django.contrib import admin
from models import *
from forms import *
from views import *

# Ajout pour definir un autre formfield_for_dbfield afin de limiter le choix du select d'un champ FK
from django import forms
# Fin de l'ajout pour definir un autre formfield_for_dbfield

# Ajout pour limiter la taille d'un champ Textfield a plus ou moins une ligne dans une section inline
from django.forms import Textarea
# Fin de l'ajout pour limiter la taille d'un champ Textfield

# Ajout pour ordering by multiple fields in a column sort
from django.contrib.admin.views.main import ChangeList
# Fin de l'ajout pour ordering by multiple fields in a column sort

from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from django.contrib.admin import widgets
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.functional import curry

"""
Usage:

import time
Afin d'avoir un changement dans les formsets de EquipModelDocInline
"""
import time

####
#
# Debut de l'ajout to order by multiple fields in a column sort
#
####
class SpecialOrderingChangeList(ChangeList):
    """
    SpecialOrderindChangeList
    """
    def apply_special_ordering(self, queryset):
        order_type, order_by = [self.params.get(param, None) for param in ('ot', 'o')]

        ordering_attr = self.model_admin.ordering or self.model._meta.ordering

        if order_type is None and order_by is None and ordering_attr != []:
            order_type = 'desc' if ordering_attr[0] == '-' else 'asc'
            order_by = self.model_admin.list_display.index(ordering_attr[0])

        special_ordering = self.model_admin.special_ordering
        if special_ordering and order_type and order_by:
            try:
                order_field = self.list_display[int(order_by)]
                ordering = special_ordering[order_field]
                if order_type == 'desc':
                    ordering = ['-' + field for field in ordering]
                queryset = queryset.order_by(*ordering)
            except IndexError:
                return queryset
            except KeyError:
                return queryset
        return queryset

    def get_query_set(self):
        queryset = super(SpecialOrderingChangeList, self).get_query_set()
        queryset = self.apply_special_ordering(queryset)
        return queryset

####
# 
# Ajouter a l'admin de la classe qui comportera un tri sur champ multiple (voir EquipmentAdmin)
#
#     special_ordering = {}
#
#     def get_changelist(self, request, **kwargs):
#         return SpecialOrderingChangeList
#
# Fin de l'ajout to order by multiple fields in a column sort
####

####
#
# ActorAdmin's section
#
####
class ActorAdmin(admin.ModelAdmin):
    list_display = ['actor_type', 'actor_name',]
    ordering = ['actor_name']
    search_fields = ['actor_name']
#    exclude = ['actor_type',]

####
#
# BuiltAdmin's section
#
####
class BuiltAdmin(admin.ModelAdmin):
    list_display = ['station', 'built_type', 'built_short_desc']
    ordering = ['station']
    search_fields = ['station__station_code']

    special_ordering = {'station': ('station__station_code', 'built_type__built_type_name')}
 
    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

####
#
# EquipmentAdmin's section
#
####
class EquipModelDocInline(admin.TabularInline):
    model = EquipModelDoc
    form = EquipModelDocInlineForm
    exclude = ['equip_supertype', 'equip_type','owner']
    extra = 1

class EquipModelAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model_name',]
    list_filter = ['equip_supertype', 'equip_type',]
    search_fields = ['equip_model_name']

    fieldsets = [('', {'fields': [('equip_supertype', 'equip_type', 'equip_model_name')]}),]

    inlines = [EquipModelDocInline]

    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """
        instances = formset.save(commit=False)
        for instance in instances:      
            if isinstance(instance, EquipModelDoc): #Check if it is the correct type of inline
                instance.equip_supertype = form.cleaned_data['equip_supertype']
                instance.equip_type = form.cleaned_data['equip_type']
                instance.save()
            else:
                formset.save()

class EquipDocInline(admin.TabularInline):
    model = EquipDoc
    form = EquipDocInlineForm
    exclude = ['equip_supertype', 'equip_type', 'equip_model','owner']
    extra = 1
    ordering = ['-inscription_date']

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number']
    list_filter = ['equip_supertype', 'equip_type', 'equip_model',]
    ordering = ['equip_supertype']
    search_fields = ['equip_model__equip_model_name', 'serial_number']
    form = EquipmentForm

    special_ordering = {'equip_supertype': ('equip_supertype__equip_supertype_name', 'equip_type__equip_type_name', 'equip_model__equip_model_name','serial_number'), 'equip_type': ('equip_type__equip_type_name', 'equip_model__equip_model_name','serial_number'), 'equip_model': ('equip_model__equip_model_name','serial_number')}
 
    fieldsets = [('Equipements', {'fields': [('equip_supertype', 'equip_type', 'equip_model', 'serial_number','owner','purchase_date','stockage_site')]}),
                 ('Information sur les contacts' , {'fields': [('contact')], 'classes': ['collapse']}),
                 ('Informations complementaires' , {'fields': [('note')], 'classes': ['collapse']}),]

    inlines = [EquipDocInline]

    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

    def save_model(self, request, obj, form, change):
        """
        Overide save_model to generate intervention and intervequip object
        Buy equipment as action and To Test for the state
        """
        obj.save()
        
        if not change:
            station_id = form.cleaned_data['stockage_site']
            purchase_date = form.cleaned_data['purchase_date']

            equipment = get_object_or_404(Equipment, pk=obj.id)
            station = get_object_or_404(StationSite, pk=station_id)

            """
            Check that intervention exist to make multiple purchase
            """
            try:
                intervention = Intervention.objects.get(station=station,intervention_date=purchase_date)
                interv_equip = IntervEquip(intervention=intervention, equip_action=EquipAction.ACHETER, \
                                           equip=equipment, equip_state=EquipState.A_TESTER, station=station, note="Creation automatique")
                interv_equip.save()
            except Intervention.DoesNotExist:
                intervention = Intervention(station=station,intervention_date=purchase_date, note="Creation automatique")
                intervention.save()
                intervention = get_object_or_404(Intervention, pk=intervention.id)
                interv_equip = IntervEquip(intervention=intervention, equip_action=EquipAction.ACHETER, \
                                           equip=equipment, equip_state=EquipState.A_TESTER, station=station, note="Creation automatique")
                interv_equip.save()
            
                actor = get_object_or_404(Actor, actor_name=request.user.username)            
                interv_actor = IntervActor(intervention=intervention, actor=actor)
                interv_actor.save()
        super(EquipmentAdmin, self).save_model(request, obj, form, change)

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
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class StationDocInline(admin.TabularInline):
    model = StationDoc
    form = StationDocInlineForm
    exclude = ['owner']
    extra = 0
    ordering = ['-inscription_date']

class StationSiteAdmin(admin.ModelAdmin):
    list_display = ('station_code', 'station_name', 'site_type', 'latitude','longitude','elevation')
    ordering = ['station_code']
    search_fields = ['station_code']
    form = StationSiteForm

    fieldsets = [
        ('Information sur la station' , {'fields': [('site_type','station_code','station_name','operator','creation_date'),('latitude','longitude','elevation')]}),
        ('Information sur les contacts' , {'fields': [('contact')], 'classes': ['collapse']}),
        ('Information sur le site' , {'fields': [('address', 'zip_code', 'city'),('department','region','country'),('note')], 'classes': ['collapse']}),]

    inlines = [BuiltInline, StationDocInline,]

    def save_model(self, request, obj, form, change):
        """
        Overide save_model to generate intervention and intervstation object
        Create station code as action and in construction for the state
        """
        obj.save()
        
        if not change:
            station = get_object_or_404(StationSite, pk=obj.id)
            intervention = Intervention(station=station,intervention_date=form.cleaned_data['creation_date'], note="Creation automatique")
	    intervention.save()
            
            intervention = get_object_or_404(Intervention, pk=intervention.id)
            interv_station = IntervStation(intervention=intervention, station_action=StationAction.CREER, station_state=StationState.INSTALLATION, note="Creation automatique")
            interv_station.save()
            
            actor = get_object_or_404(Actor, actor_name=request.user.username)            
            interv_actor = IntervActor(intervention=intervention, actor=actor)
            interv_actor.save()
        super(StationSiteAdmin, self).save_model(request, obj, form, change)

####
#
# Table code Admin's section
#
####

class EquipTypeAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type_name',]
    list_filter = ['equip_supertype',]

class IntervActorInline(admin.TabularInline):
    model = IntervActor
    extra = 0
    formset = IntervActorInlineFormset

    def get_formset(self, request, obj=None, **kwargs):
        initial = []
        if obj is not None:
            kwargs['extra'] = 0
        else:
            kwargs['extra'] = 1
            """
            Pre-populating formset using GET params
            """
            initial.append(request.user.username)
        formset = super(IntervActorInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class IntervStationInline(admin.TabularInline):
    model = IntervStation
    extra = 0
    max_num = 1
    formset = IntervStationInlineFormset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class IntervEquipInline(admin.TabularInline):
    model = IntervEquip
    extra = 0
    formset = IntervEquipInlineFormset

    def get_formset(self, request, obj=None, **kwargs):
        station = request.GET.get('station', '') 
        equip = request.GET.get('equip', '') 
        initial = []
        if obj is not None:
            kwargs['extra'] = 0
        else:
            kwargs['extra'] = 1
            """
            Pre-populating formset using GET params
            """
            initial.append(request.user.username)
        formset = super(IntervEquipInline, self).get_formset(request, obj, **kwargs)
#        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class InterventionAdmin(admin.ModelAdmin):
    list_display = ['station', 'intervention_date',]

    inlines = [IntervActorInline, IntervStationInline, IntervEquipInline]

    class Media:
        js = ["my_ajax_function.js"]

######## class ChainComponentInlineFormset(forms.models.BaseInlineFormSet):
########  
########    def clean(self):
########        """Checks that equipment exist for the station."""
########        if any(self.errors):
########            # Don't bother validating the formset unless each form is valid on its own
########            return
######## 
########        for i in range(0, self.total_form_count()):
########            form = self.forms[i]
######## #           print u'Cleaned_data : %s' % (form.cleaned_data)
########            if form.cleaned_data != {}:
########                acqui_chain = form.cleaned_data['acquisition_chain']
########                L = [equip.equip_id for equip in HistoricStationEquip.objects.filter(station=acqui_chain.station)]
########                equip = form.cleaned_data['equip']
########                if equip.id not in L:
########                    raise forms.ValidationError("Equipement choisi non present dans la station.")

######## class ChainComponentInline(admin.TabularInline):
########     model = ChainComponent
########     formset = ChainComponentInlineFormset
########     extra = 0
######## 
########     def get_formset(self, request, obj=None, **kwargs):
########         # Hack! Hook parent obj just in time to use in formfield_for_manytomany
########         self.parent_obj = obj
######## #        if self.parent_obj: 
######## #            print obj.__class__.__name__
########         return super(ChainComponentInline, self).get_formset(
########             request, obj, **kwargs)
########  
######## """ 
########     Pour limiter dans le choix du select de la FK que les equipements de la station 
########     """
######## 
########     def formfield_for_dbfield(self, field, **kwargs):
########         if field.name == 'equip':
########             if self.parent_obj :
########                 parent_station = self.parent_obj
########                 L = [equip.equip_id for equip in HistoricStationEquip.objects.filter(station=parent_station.station)]
########                 contained_equip = Equipment.objects.filter(id__in = L)
########                 return forms.ModelChoiceField(label="equipement",queryset=contained_equip, required=True)    
########         return super(ChainComponentInline, self).formfield_for_dbfield(field, **kwargs)

######## class ChannelInline(admin.TabularInline):
########     model = Channel
########     extra = 0
 
######## class AcquisitionChainAdmin(admin.ModelAdmin):
########     inlines = [ChainComponentInline, ChannelInline]

######## class ChannelAdmin(admin.ModelAdmin):
######## list_display = ['network', 'acquisition_chain', 'channel_code', 'dip', 'azimuth', 'sample_rate', 'start_date']

admin.site.register(Actor, ActorAdmin)
#admin.site.register(Built, BuiltAdmin)
#admin.site.register(BuiltType)

admin.site.register(EquipModel, EquipModelAdmin)
admin.site.register(Equipment, EquipmentAdmin)

admin.site.register(StationSite, StationSiteAdmin)
#admin.site.register(StationDoc, StationDocAdmin)
#admin.site.register(EquipModelDoc, EquipModelDocAdmin)
#admin.site.register(EquipDoc, EquipDocAdmin)

######## admin.site.register(AcquisitionChain,AcquisitionChainAdmin)
######## admin.site.register(ChainComponent)
######## admin.site.register(Channel, ChannelAdmin)

admin.site.register(Intervention, InterventionAdmin)
