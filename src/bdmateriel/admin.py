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

from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode

from django.contrib.admin import widgets
from django.shortcuts import render_to_response, get_object_or_404, HttpResponseRedirect
from django.utils.functional import curry

# Ajout pour custom filter
from django.contrib.admin import SimpleListFilter
# Fin de l'ajout pour custom filter
"""
Usage:

import time
Afin d'avoir un changement dans les formsets de EquipModelDocInline
"""
import time

# Ajout pour custom URLFieldWidget
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe
# Fin de l'ajout pour custom URLFieldWidget

class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<input type="button" '
                         u'value="View Link" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value)" />' % (widget, attrs['id']))

####
#
# ActorAdmin's section
#
####
class ActorAdmin(admin.ModelAdmin):
    list_display = ['actor_type', 'actor_name',]
    list_display_links = ['actor_name',]
    ordering = ['actor_type', 'actor_name',]
    search_fields = ['actor_name',]
#    exclude = ['actor_type',]

####
#
# BuiltAdmin's section
#
####
class BuiltAdmin(admin.ModelAdmin):
    list_display = ['station', 'built_type', 'built_short_desc',]
    ordering = ['station',]
    search_fields = ['station__station_code',]

####
#
# EquipmentAdmin's section
#
####
class EquipModelDocInline(admin.TabularInline):
    model = EquipModelDoc
    form = EquipModelDocInlineForm
    exclude = ['equip_supertype', 'equip_type','owner',]
    extra = 1

"""
Custom filter for the equipment model change list
"""
class EquipModelFilter(SimpleListFilter):
   # Human-readable title which will be displayed in the
   # right admin sidebar just above the filter options.
   title = _('Supertype or Type')

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
       Equip_Supertype = EquipSupertype.objects.all().order_by('equip_supertype_name')
       

       """
       Tree presentation of the filter choice.
       Indentation by space character unichr(160) and to distinguish
       the equipment type we enclose it by <>
       and equipment model by []
       """
       for equip_supertype in Equip_Supertype:
           Liste.append(('Stype_'+str(equip_supertype.id), _(equip_supertype.equip_supertype_name)))
           Equip_Type = EquipType.objects.filter(equip_supertype=equip_supertype).order_by('equip_type_name')
           for equip_type in Equip_Type:
               Liste.append(('Type__'+str(equip_type.id), _(equip_type.equip_type_name)))
       return Liste

   def queryset(self, request, queryset):
       """
       Returns the filtered queryset based on the value
       provided in the query string and retrievable via
       `self.value()`.
       """
       if self.value():
           if self.value()[:5] == 'Stype':
               return queryset.filter(equip_supertype__id__exact=self.value()[6:])
           if self.value()[:5] == 'Type_':
               return queryset.filter(equip_type__id__exact=self.value()[6:])

class EquipModelAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model_name',]
    list_display_links = ['equip_model_name',]
    list_filter = [EquipModelFilter,]
    ordering = ['equip_supertype', 'equip_type', 'equip_model_name',]
    search_fields = ['equip_model_name',]

    fieldsets = [('', {'fields': [('equip_supertype', 'equip_type', 'equip_model_name')]}),]

    inlines = [EquipModelDocInline,]

    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """
        instances = formset.save(commit=False)
        for instance in instances:      
            if isinstance(instance, EquipModelDoc): #Check if it is the correct type of inline
                instance.equip_supertype = form.cleaned_data['equip_supertype']
                instance.equip_type = form.cleaned_data['equip_type']
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()

class EquipDocInline(admin.TabularInline):
    model = EquipDoc
    form = EquipDocInlineForm
    exclude = ['equip_supertype', 'equip_type', 'equip_model','owner']
    extra = 1
    ordering = ['-inscription_date']

"""
Custom filter for the equipment change list
"""
class EquipFilter(SimpleListFilter):
   # Human-readable title which will be displayed in the
   # right admin sidebar just above the filter options.
   title = _('Supertype, Type or Model')

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
       Liste = []
       Equip_Supertype = EquipSupertype.objects.all().order_by('equip_supertype_name')

       """
       Tree presentation of the filter choice.
       Indentation by space character unichr(160) and to distinguish
       the equipment type we enclose it by <>
       and equipment model by []
       """
       for equip_supertype in Equip_Supertype:
           Liste.append(('Stype_'+str(equip_supertype.id), _(equip_supertype.equip_supertype_name)))
           Equip_Type = EquipType.objects.filter(equip_supertype=equip_supertype).order_by('equip_type_name')
           for equip_type in Equip_Type:
               Liste.append(('Type__'+str(equip_type.id), _(equip_type.equip_type_name)))
               Equip_Model = EquipModel.objects.filter(equip_supertype=equip_supertype,equip_type=equip_type).order_by('equip_model_name')
               for equip_model in Equip_Model:
                   Liste.append(('Model_'+str(equip_model.id), _(equip_model.equip_model_name)))
       return Liste

   def queryset(self, request, queryset):
       """
       Returns the filtered queryset based on the value
       provided in the query string and retrievable via
       `self.value()`.
       """
       if self.value():
           if self.value()[:5] == 'Stype':
               return queryset.filter(equip_supertype__id__exact=self.value()[6:])
           if self.value()[:5] == 'Type_':
               return queryset.filter(equip_type__id__exact=self.value()[6:])
           if self.value()[:5] == 'Model':
               return queryset.filter(equip_model__id__exact=self.value()[6:])

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number', 'get_last_state', 'get_last_place', 'owner',]
    list_display_links = ['serial_number',]
#    list_filter = ['equip_supertype', 'equip_type', 'equip_model',]
    list_filter = [EquipFilter,]
    ordering = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number',]
    search_fields = ['equip_model__equip_model_name', 'serial_number',]
    form = EquipmentForm

    fieldsets = [('Equipements', {'fields': [('equip_supertype', 'equip_type', 'equip_model', 'serial_number','owner','purchase_date','stockage_site')]}),
                 ('Information sur les contacts' , {'fields': [('contact')], 'classes': ['collapse']}),
                 ('Informations complementaires' , {'fields': [('note')], 'classes': ['collapse']}),]

    inlines = [EquipDocInline,]

    def get_last_state(self, obj):
        return '%s'%(equip_last_state(obj.id))
    get_last_state.short_description = 'Etat'

    def get_last_place(self, obj):
        return '%s'%(equip_last_place(obj.id))
    get_last_place.short_description = 'Emplacement'

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

    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """
        instances = formset.save(commit=False)
        for instance in instances:      
            if isinstance(instance, EquipDoc): #Check if it is the correct type of inline
                instance.equip_supertype = form.cleaned_data['equip_supertype']
                instance.equip_type = form.cleaned_data['equip_type']
                instance.equip_model = form.cleaned_data['equip_model']
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()

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
    exclude = ['owner',]
    extra = 0
    ordering = ['-inscription_date',]

"""
Custom filter for the stationsite change list
"""
class StationSiteFilter(SimpleListFilter):
   # Human-readable title which will be displayed in the
   # right admin sidebar just above the filter options.
   title = _('Operateur')

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
       Operator_station = StationSite.objects.values_list('operator',flat=True)
       liste_val_distinct_triee = list(sorted(set(Operator_station)))

       Operator = Actor.objects.filter(id__in=liste_val_distinct_triee).order_by('actor_name')

       """
       Tree presentation of the filter choice.
       """
       for operator in Operator:
           Liste.append(((str(operator.id)), _(operator.actor_name)))
       return Liste

   def queryset(self, request, queryset):
       """
       Returns the filtered queryset based on the value
       provided in the query string and retrievable via
       `self.value()`.
       """
       if self.value():
           return queryset.filter(operator__id__exact=self.value())

#import copy

#def copy_stationsite(modeladmin, request, queryset):
#    # sd is an instance of StationSite
#    for sd in queryset:
#        sd_copy = copy.copy(sd) # (2) django copy object
#        sd_copy.id = None   # (3) set 'id' to None to create new object
#        sd_copy.station_code = sd.station_code + '_NEW' 
#        sd_copy.save()    # initial save
#
#    copy_stationsite.short_description = "Make a Copy of StationSite"

class StationSiteAdmin(admin.ModelAdmin):
#    actions = [copy_stationsite]
    list_display = ('station_code', 'station_name', 'operator', 'get_last_state', 'site_type', 'latitude', 'longitude', 'elevation',)
    list_filter = [StationSiteFilter,  'site_type',]
    ordering = ['station_code',]
    search_fields = ['station_code',]
    form = StationSiteForm

    fieldsets = [
        ('Information sur le site' , {'fields': [('site_type','station_code','station_name', 'station_parent', 'operator','creation_date'),('latitude','longitude','elevation')]}),
        ('Information sur les contacts' , {'fields': [('contact')], 'classes': ['collapse']}),
        ('Adresse du site' , {'fields': [('address', 'zip_code', 'city'),('department','region','country')], 'classes': ['collapse']}),
        ('Autre information pertinente' , {'fields': [('note'),('private_link')], 'classes': ['collapse']}),]

    inlines = [BuiltInline, StationDocInline,]

    def get_last_state(self, obj):
        """ To display the last state of the station in the change_list """
        return '%s'%(station_last_state(obj.id))
    get_last_state.short_description = 'Etat'

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

    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """
        instances = formset.save(commit=False)
        for instance in instances:      
            if isinstance(instance, StationDoc): #Check if it is the correct type of inline
                if not instance.pk:
                    instance.owner = request.user
                instance.save()
            else:
                formset.save()

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

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
#    readonly_fields=['equip', 'station', 'built', 'note',]

    def get_formset(self, request, obj=None, **kwargs):
        """ Pourquoi est-ce que station est necessaire """
        station = request.GET.get('station', '') 
        equip = request.GET.get('equip', '') 
        initial = []
        initial.append(equip)
#        if obj is not None:
#            kwargs['extra'] = 0
#        else:
#            kwargs['extra'] = 1
#            """
#            Pre-populating formset using GET params
#            """
#            initial.append(equip)
        formset = super(IntervEquipInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class InterventionAdmin(admin.ModelAdmin):
    list_display = ['station', 'intervention_date',]
    list_filter = ['station',]
    ordering = ['-intervention_date',]
    form = InterventionForm

    inlines = [IntervActorInline, IntervStationInline, IntervEquipInline]

    class Media:
        js = ["js/my_ajax_function.js"]

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_stationsite_change", args=(obj.station.id,)))
        else:
            return super(InterventionAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_stationsite_change", args=(obj.station.id,)))
        else:
            return super(InterventionAdmin, self).response_add(request, obj, post_url_continue)

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


class ChainInline(admin.TabularInline):
    model = Chain
    extra = 0
    formset = ChainInlineFormset

    readonly_fields = ['configuration']

    def configuration(self, obj):
        if obj.id:
            url = reverse('admin:bdmateriel_chain_change', args=[obj.id])
            return mark_safe("<a href='%s'>config</a>" % url)

    def get_formset(self, request, obj=None, **kwargs):
#       Pourquoi est-ce que station est necessaire
        station = request.GET.get('station', '') 
        initial = []
        initial.append(station)
        formset = super(ChainInline, self).get_formset(request, obj, **kwargs)
        formset.__init__ = curry(formset.__init__, initial=initial)
        return formset

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

from django.contrib import messages

class ChannelAdmin(admin.ModelAdmin):
    model = Channel
    save_as = True
    form = ChannelForm

    fieldsets = [
        ('' , {'fields': [('station','latitude','longitude','elevation','depth', 'azimuth', 'dip'),('network','channel_code','location_code'),('sample_rate', 'start_date', 'end_date')]}),]

    inlines = [ChainInline,]

# a lot of todo 
# blinder la generation automatique de parametre de config selon modele equip
# empecher tout changement
# generer l'ordre automatiquement

    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """
        instances = formset.save(commit=False)
        
        for instance in instances:
            if isinstance(instance, Chain): #Check if it is the correct type of inline
                instance.save()
                parameters = ParamEquipModel.objects.filter(equip_model_id=instance.equip.equip_model.id).order_by('pk')
                for parameter in parameters:
                    chainconfig = ChainConfig(chain=instance,parameter=parameter.parameter_name, value=parameter.default_value)
                    chainconfig.save()
            else:
                formset.save()               

    class Media:
        js = ["js/my_ajax_function.js"]

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_stationsite_change", args=(obj.station.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success( request, 'Enregistrement modifié' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChannelAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_stationsite_change", args=(obj.station.id,)))
        else:
##        This makes the response go to the newly created model's change page
##        without using reverse
            if '_saveasnew' in request.POST:              
                messages.success( request, 'Enregistrement ajouté' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChannelAdmin, self).response_add(request, obj, post_url_continue)

class ChainConfigInline(admin.TabularInline):
    model = ChainConfig
    extra = 0

    fields = ('parameter', 'value')

class ChainAdmin(admin.ModelAdmin):
    model = Chain

    readonly_fields = ['channel','order','equip']

    inlines = [ChainConfigInline,]
        
admin.site.register(Channel, ChannelAdmin)
admin.site.register(Chain, ChainAdmin)
#admin.site.register(ProtoConfig)


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
