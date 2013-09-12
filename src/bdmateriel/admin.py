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

class LabeledHiddenInput(forms.HiddenInput):
    def render(self, name, value, attrs=None):

        status  = self.choices.queryset.get(pk = value)
        
        h_input = super(LabeledHiddenInput, self).render( name, value, attrs=None)
        return mark_safe("%s %s"%(status, h_input))

####
#
# ActorAdmin's section
#
####
class ActorAdmin(admin.ModelAdmin):
    form = ActorForm
    list_display = ['actor_parent', 'actor_name', 'actor_type',]
    list_display_links = ['actor_name',]
    ordering = ['actor_parent', 'actor_name',]
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
    fields = ('document_type', 'document_title', 'begin_effective', 'end_effective', 'document_equip_model', 'private_link')
    form = EquipModelDocInlineForm
    exclude = ['equip_supertype', 'equip_type','owner',]
    extra = 0
    ordering = ['-begin_effective',]

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

class ParamEquipModelInline(admin.TabularInline):
    model = ParamEquipModel
    extra = 0

class ParameterEquipInline(admin.TabularInline):
    model = ParameterEquip
    extra = 0

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
    list_filter = [EquipModelFilter, ]
    ordering = ['equip_supertype', 'equip_type', 'equip_model_name',]
    search_fields = ['equip_model_name',]

    fieldsets = [('', {'fields': [('equip_supertype', 'equip_type', 'equip_model_name', 'manufacturer')]}),]

    inlines = [EquipModelDocInline, ParameterEquipInline,]

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
    fields = ('document_type', 'document_title', 'begin_effective', 'end_effective', 'document_equip', 'private_link')
    form = EquipDocInlineForm
    exclude = ['equip_supertype', 'equip_type', 'equip_model','owner']
    extra = 0
    ordering = ['-begin_effective']

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

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
       liste = []
       Equip_Supertype = EquipSupertype.objects.all().order_by('equip_supertype_name')

       """
       Tree presentation of the filter choice.
       Indentation by space character unichr(160) and to distinguish
       the equipment type we enclose it by <>
       and equipment model by []
       """
       for equip_supertype in Equip_Supertype:
           liste.append(('Stype_'+str(equip_supertype.id), _(equip_supertype.equip_supertype_name)))
           Equip_Type = EquipType.objects.filter(equip_supertype=equip_supertype).order_by('equip_type_name')
           for equip_type in Equip_Type:
               liste.append(('Type__'+str(equip_type.id), _(equip_type.equip_type_name)))
               Equip_Model = EquipModel.objects.filter(equip_supertype=equip_supertype,equip_type=equip_type).order_by('equip_model_name')
               for equip_model in Equip_Model:
                   liste.append(('Model_'+str(equip_model.id), _(equip_model.equip_model_name)))
       return liste

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

class OwnerFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('owner')

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
        lookup_list = Actor.objects.filter(Q(actor_type=Actor.OBSERVATOIRE) | Q(actor_type=Actor.ORGANISME) | Q(actor_type=Actor.INCONNU)).values_list('id', 'actor_name').distinct() 
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
    list_display = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number', 'get_last_state', 'get_last_place', 'owner',]
    list_display_links = ['serial_number',]
#    list_filter = ['equip_supertype', 'equip_type', 'equip_model',]
    list_filter = [EquipFilter, ]
    ordering = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number',]
    search_fields = ['equip_model__equip_model_name', 'serial_number',]
    form = EquipmentForm

    fieldsets = [('Equipements', {'fields': [('equip_supertype', 'equip_type', 'equip_model', 'serial_number','owner','purchase_date','stockage_site')]}),
                 ('Information sur les contacts' , {'fields': [('vendor', 'contact')], 'classes': ['collapse']}),
                 ('Informations complementaires' , {'fields': [('note')], 'classes': ['collapse']}),]

    inlines = [EquipDocInline,]

    def get_last_state(self, obj):
        return '%s'%(equip_last_state(obj.id))
    get_last_state.short_description = 'Etat'

    def get_last_place(self, obj):
        return '%s'%(equip_last_place(obj.id))
    get_last_place.short_description = 'Emplacement'

    # Redefine queryset to show only equipment according to the user's project
    def queryset(self, request):
        qs = super(EquipmentAdmin, self).queryset(request)
        check_forall = ProjectUser.objects.filter(user=request.user).values_list('project__project_name', flat=True)
        # The name of the project must stay ALL
        if request.user.is_superuser or u'ALL' in check_forall:
            return qs
        project_list = ProjectUser.objects.filter(user=request.user).values_list('project', flat=True)
        station_list = Project.objects.filter(id__in=project_list).values_list('station', flat=True)
        intervequip_list = IntervEquip.objects.filter(station_id__in=station_list).values_list('equip', flat=True).distinct()
        return qs.filter(id__in=intervequip_list)

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
    fields = ('document_type', 'document_title', 'begin_effective', 'end_effective', 'document_station', 'private_link')
    form = StationDocInlineForm
    exclude = ['owner',]
    extra = 0
    ordering = ['-begin_effective',]

    formfield_overrides = {
        models.URLField: {'widget': URLFieldWidget},
    }

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
    list_display = ('station_code', 'site_name', 'operator', 'get_last_state', 'site_type', 'latitude', 'longitude', 'elevation',)
    list_filter = [StationSiteFilter,  'site_type',]
    ordering = ['station_code',]
    search_fields = ['station_code', 'site_name', 'operator__actor_name']
    form = StationSiteForm

    fieldsets = [
        ('Information sur le site' , {'fields': [('site_type','station_code','site_name','station_parent','operator','creation_date','project'),('latitude','longitude','elevation'),('geology')]}),
        ('Information sur les contacts' , {'fields': [('contact')], 'classes': ['collapse']}),
        ('Adresse du site' , {'fields': [('site_description'),('address', 'zip_code', 'town'),('county','region','country')], 'classes': ['collapse']}),
        ('Autre information pertinente' , {'fields': [('note'),('private_link')], 'classes': ['collapse']}),
        ('Informations complementaires' , {'fields': [('station_description'),('alternate_code','historical_code','restricted_status')], 'classes': ['collapse']}),]

    inlines = [BuiltInline, StationDocInline,]

    def get_last_state(self, obj):
        """ To display the last state of the station in the change_list """
        return '%s'%(station_last_state(obj.id))
    get_last_state.short_description = 'Etat'

    def get_form(self, request, obj=None, **kwargs):
         form = super(StationSiteAdmin, self).get_form(request, obj, **kwargs)
         form.current_user = request.user
         return form

    # Redefine queryset to show only site according to the user's project
    def queryset(self, request):
        qs = super(StationSiteAdmin, self).queryset(request)
        check_forall = ProjectUser.objects.filter(user=request.user).values_list('project__project_name', flat=True)
        # The name of the project must stay ALL
        if request.user.is_superuser or u'ALL' in check_forall:        
            return qs
        project_list = ProjectUser.objects.filter(user=request.user).values_list('project', flat=True)
        station_list = Project.objects.filter(id__in=project_list).values_list('station', flat=True)
        return qs.filter(id__in=station_list)

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

            #Each new station will be store in Resif by default
            project_object = get_object_or_404(Project, project_name=form.cleaned_data['project'])
            project_object.station.add(obj.id)
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
#    Test of the modified tabular template to hide the Add at the inline
#    template = 'tabulartest.html'

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
    list_display = ['station', 'format_date']
    list_filter = ['station',]
    ordering = ['station', '-intervention_date',]
    search_fields = ['station__station_code', 'intervention_date',]
    form = InterventionForm

    inlines = [IntervActorInline, IntervStationInline, IntervEquipInline]

    class Media:
        js = ["js/my_ajax_function.js"]

    # Redefine queryset to show only intervention according to the user's project
    def queryset(self, request):
        qs = super(InterventionAdmin, self).queryset(request)
        check_forall = ProjectUser.objects.filter(user=request.user).values_list('project__project_name', flat=True)
        # The name of the project must stay ALL
        if request.user.is_superuser or u'ALL' in check_forall:
            return qs
        project_list = ProjectUser.objects.filter(user=request.user).values_list('project', flat=True)
        station_list = Project.objects.filter(id__in=project_list).values_list('station', flat=True)
        return qs.filter(station_id__in=station_list)

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

    def format_date(self, obj):
        return obj.intervention_date.strftime('%Y-%m-%d %H:%M')
    format_date.short_description = 'Date (aaaa-mm-jj hh24:mi)'
    format_date.admin_order_field = 'intervention_date'

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
            # Hack to obtain the channel ID to be able to pass it to the config link as parameter
            channel = get_object_or_404(Chain, pk=obj.id).channel.id
            url = reverse('admin:bdmateriel_chain_change', args=[obj.id]) + '?channel=' +str(channel)
            return mark_safe("<a href='%s'>config</a>" % url)

    def delete(self, obj):
        if obj.id:
            url = reverse('admin:bdmateriel_chain_change', args=[obj.id]) + 'delete/'
            return mark_safe("<a href='%s'>delete</a>" % url)

    def get_formset(self, request, obj=None, **kwargs):
#       Pourquoi est-ce que station est necessairen
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

"""
class ChainConfigInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
#    formset = ChainConfigInlineFormset

    fields = ('parameter', 'value')

    # Hack to pass the channel id to the formset
#    def get_formset(self, request, obj=None, **kwargs):
#        channel = request.GET.get('channel', '') 
#        initial = []
#        initial.append(channel)
#        formset = super(ChainConfigInline, self).get_formset(request, obj, **kwargs)
#        formset.__init__ = curry(formset.__init__, initial=initial)
#        return formset
"""

class ChainConfigInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
    formset = ChainConfigInlineFormset

    fields = ('parameter', 'value')

"""
class ChannelChainInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
    max_num = 0

#    readonly_fields = ['chain']
    fields = ('chain', 'parameter', 'value')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'chain': #on suppose que le modele a un champ image
            kwargs['widget'] = forms.TextInput(attrs={'readonly':'readonly','style':'width: 1px'})
#            kwargs['widget'] = forms.HiddenInput()
            kwargs.pop('request', None) #erreur sinon
            return db_field.formfield(**kwargs)
        return super(ChannelChainInline,self).formfield_for_dbfield(db_field, **kwargs)
"""

class ChannelChainInline(admin.TabularInline):
    model = ChainConfig
    extra = 0
    max_num = 0
    formset = ChannelChainInlineFormset

#    readonly_fields = ['chain']
    fields = ('chain', 'parameter', 'value')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'chain': #on suppose que le modele a un champ image
            kwargs['widget'] = forms.TextInput(attrs={'readonly':'readonly','style':'width: 1px'})
#            kwargs['widget'] = forms.HiddenInput()
            kwargs.pop('request', None) #erreur sinon
            return db_field.formfield(**kwargs) 
        return super(ChannelChainInline,self).formfield_for_dbfield(db_field, **kwargs)

class ChannelAdmin(admin.ModelAdmin):
    model = Channel
    save_as = True
    form = ChannelForm

#    list_display = ['network', 'station', 'channel_code', 'location_code', 'start_date','end_date']
#    list_editable = ['end_date' ]

    actions = ['delete_selected']

    fieldsets = [
        ('' , {'fields': [('network','station','channel_code','location_code'),('latitude','longitude','elevation','depth','azimuth','dip'),('sample_rate', 'accept_anyway', 'start_date','end_date')]}),
        ('Types des donnees produites', {'fields': [('data_type')], 'classes': ['collapse']}),
        ('Informations complementaires' , {'fields': [('description'),('alternate_code','historical_code','restricted_status'),('storage_format','clock_drift','calibration_units')], 'classes': ['collapse']}),]

    inlines = [ChainInline, ChannelChainInline]
#    inlines = [ChainInline,]

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
                # TODO Find how to access the previous channel to recuparate the config of some equipments.
                # Actually we add the default config.
                if not '_saveasnew' in request.POST:
                    #parameters = ParamEquipModel.objects.filter(equip_model_id=instance.equip.equip_model.id).order_by('pk')
                    parameters = ParameterValue.objects.filter(parameter__equip_model_id=instance.equip.equip_model.id, default_value=True).order_by('pk')
                    """
                    for parameter in parameters:
                        channel = get_object_or_404(Channel, pk=instance.channel.id) # Hack to inline in channel
                        #Default physical channel according to the channel code and network code
                        chainconfig = ChainConfig(channel=channel,chain=instance,parameter=parameter.parameter_name, value=parameter.default_value)
                        chainconfig.save()
                    """    
                    for parameter in parameters:
                        channel = get_object_or_404(Channel, pk=instance.channel.id) # Hack to inline in channel
                        """
                        Default value for config parameter
                        """
                        chainconfig = ChainConfig(channel=channel,chain=instance,parameter=parameter.parameter, value=parameter)
                        chainconfig.save()
            else:
                if isinstance(instance, ChainConfig): #Check if it is the correct type of inline
                    old_chain = get_object_or_404(Chain, pk=instance.chain.id) # Hack to inline in channel
                    new_chain = Chain.objects.filter(channel=instance.channel.id, order=old_chain.order, equip=old_chain.equip) # Hack to inline in channel
                    if new_chain:
                        instance.chain = new_chain[0]
                    instance.save()
                else:
                    formset.save()               
                """                    
                else:
                    if isinstance(instance, ChainConfigTest): #Check if it is the correct type of inline
                        old_chain = get_object_or_404(Chain, pk=instance.chain.id) # Hack to inline in channel
                        new_chain = Chain.objects.filter(channel=instance.channel.id, order=old_chain.order, equip=old_chain.equip) # Hack to inline in channel
                        if new_chain:
                            instance.chain = new_chain[0]
                        instance.save()
                """                        

#    def save_model(self, request, obj, form, change):
#        # custom stuff here
#        if '_saveasnew' in request.POST:
#            print "I am saved_as new save"
#            print obj
#            print request
#            obj.save()
#        else:
#            print "Other save method save"
#            obj.save()

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

class ChainAdmin(admin.ModelAdmin):
    model = Chain

    readonly_fields = ['channel','order','equip']

    inlines = [ChainConfigInline, ]

    class Media:
        js = ["js/my_ajax_function.js"]

    # This put the channel into the ChainConfig instance according with the channel value pass through the URL
    def save_formset(self, request, form, formset, change):
        """ Reference du code
            http://stackoverflow.com/questions/3016158/django-inlinemodeladmin-set-inline-field-from-request-on-save-set-user-field """

        instances = formset.save(commit=False)
 
        for instance in instances:
            if isinstance(instance, ChainConfig): #Check if it is the correct type of inline
                if not instance.pk:
                    instance.channel = instance.chain.channel
                instance.save()
            else:
                formset.save()
            """                
            else:
                if isinstance(instance, ChainConfigTest): #Check if it is the correct type of inline
                    if not instance.pk:
                        instance.channel = instance.chain.channel
                    instance.save()
            """                    

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_channel_change", args=(obj.channel.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success( request, 'Enregistrement modifié' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChainAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_channel_change", args=(obj.channel.id,)))
        else:
##        This makes the response go to the newly created model's change page
##        without using reverse
            if '_saveasnew' in request.POST:              
                messages.success( request, 'Enregistrement ajouté' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ChainAdmin, self).response_add(request, obj, post_url_continue)

class CommentNetworkAuthorInline(admin.TabularInline):
    model = CommentNetworkAuthor
    extra = 0

class CommentNetworkAdmin(admin.ModelAdmin):
    model = CommentNetwork

    fieldsets = [
        ('' , {'fields': [('network','begin_effective','end_effective'),('value')]})]

    inlines = [CommentNetworkAuthorInline,]

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_network_change", args=(obj.network.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success( request, 'Enregistrement modifié' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(CommentNetworkAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_network_change", args=(obj.network.id,)))
        else:
##        This makes the response go to the newly created model's change page
##        without using reverse
            if '_saveasnew' in request.POST:              
                messages.success( request, 'Enregistrement ajouté' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(CommentNetworkAdmin, self).response_add(request, obj, post_url_continue)


class NetworkAdmin(admin.ModelAdmin):
    model = Network
    ordering = ['network_code',]

    fieldsets = [
        ('' , {'fields': [('network_code','start_date','end_date'),]}),
        ('Informations complementaires' , {'fields': [('description'), ('alternate_code','historical_code', 'restricted_status')], 'classes': ['collapse']}),]
        
class CommentChannelAuthorInline(admin.TabularInline):
    model = CommentChannelAuthor
    extra = 0

class CommentChannelAdmin(admin.ModelAdmin):
    model = CommentChannel

    fieldsets = [
        ('' , {'fields': [('channel','begin_effective','end_effective'),('value')]})]

    inlines = [CommentChannelAuthorInline,]

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_channel_change", args=(obj.channel.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success( request, 'Enregistrement modifié' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(CommentChannelAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_channel_change", args=(obj.channel.id,)))
        else:
##        This makes the response go to the newly created model's change page
##        without using reverse
            if '_saveasnew' in request.POST:              
                messages.success( request, 'Enregistrement ajouté' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(CommentChannelAdmin, self).response_add(request, obj, post_url_continue)

class CommentStationSiteAuthorInline(admin.TabularInline):
    model = CommentStationSiteAuthor
    extra = 0

class CommentStationSiteAdmin(admin.ModelAdmin):
    model = CommentStationSite

    fieldsets = [
        ('' , {'fields': [('station','begin_effective','end_effective'),('value')]})]

    inlines = [CommentStationSiteAuthorInline,]

    def response_change(self, request, obj):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement modifié' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_stationsite_change", args=(obj.station.id,)))
        else:
            if '_saveasnew' in request.POST:
                messages.success( request, 'Enregistrement modifié' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(CommentStationSiteAdmin, self).response_change(request, obj)

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
                return super(CommentStationSiteAdmin, self).response_add(request, obj, post_url_continue)


class ProjectAdmin(admin.ModelAdmin):
    model = Project
    filter_horizontal = ['station',]
    fields = ('project_name', 'manager','station')
    
    # Redefine queryset to show only project according to the user's project
    def queryset(self, request):
        qs = super(ProjectAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(manager_id=request.user.id)

    def delete_model(self, request, obj):
        if obj.project_name == 'ALL':
            messages.error( request, 'Delete of the project ALL is forbidden')            
        else:
            obj.delete()
            return super(ProjectAdmin, self).delete_model(request, obj)

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
            return ('project_name', 'manager')
        return self.readonly_fields

class ProjectUserAdmin(admin.ModelAdmin):
    model = ProjectUser
    form = ProjectUserForm

    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple, 'queryset': Project.objects.all().order_by('project_name')},
    }

    # Redefine queryset to show only intervention according to the user's project
    def queryset(self, request):
        qs = super(ProjectUserAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(user_id=request.user.id)

"""
class ParamValueEquipModelAdmin(admin.ModelAdmin):
    model = ParamValueEquipModel
    save_as = True
    list_display = ['equip_model', 'parameter_name', 'value', 'default_value',]
    list_filter = ['equip_model', ]
    search_fields = ['equip_model', ]

    def response_add(self, request, obj, post_url_continue="../%s/"):
        if not '_continue' in request.POST and not '_saveasnew' in request.POST and not '_addanother' in request.POST:
            messages.success( request, 'Enregistrement ajouté' )
            return HttpResponseRedirect(reverse("admin:bdmateriel_paramvalueequipmodel_change", args=(obj.station.id,)))
        else:
##        This makes the response go to the newly created model's change page
##        without using reverse
            if '_saveasnew' in request.POST:              
                messages.success( request, 'Enregistrement ajouté' )
                return HttpResponseRedirect("../%s" % obj.id)
            else:
                return super(ParamValueEquipModelAdmin, self).response_add(request, obj, post_url_continue)
"""
"""
class ParamEquipModelAdmin(admin.ModelAdmin):
    model = ParamEquipModel

    inlines = [ParamValueInline,]
"""    

class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 0

class ParameterEquipAdmin(admin.ModelAdmin):
    model = ParameterEquip
    search_fields = ['equip_model__equip_model_name', 'parameter_name', ]

    list_display = ['equip_model', 'parameter_name',]

    inlines = [ ParameterValueInline,]

class ParameterValueAdmin(admin.ModelAdmin):
    model = ParameterValue
    list_filter = ['parameter', ]
    search_fields = ['parameter__equip_model__equip_model_name', 'parameter__parameter_name', ]

    list_display = ['parameter', 'value', 'default_value' ]
    list_editable = ['default_value' ]

class ChannelCodeAdmin(admin.ModelAdmin):
    model = ChannelCode
    search_fields = ['channel_code', ]

    list_display = ['channel_code', 'presentation_rank', ]

"""
Disabling the action "delete_selected" for all the site
"""
admin.site.disable_action('delete_selected')


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

admin.site.register(Network, NetworkAdmin)
admin.site.register(BuiltType)
admin.site.register(CalibrationUnit)
admin.site.register(DataType)
admin.site.register(ParamEquipModel)
#admin.site.register(ParamValueEquipModel, ParamValueEquipModelAdmin)
#admin.site.register(ParamValue)
admin.site.register(EquipModelDocType)
admin.site.register(EquipDocType)
admin.site.register(StationDocType)

admin.site.register(EquipType)

admin.site.register(Intervention, InterventionAdmin)
admin.site.register(CommentNetwork, CommentNetworkAdmin)
admin.site.register(CommentChannel, CommentChannelAdmin)
admin.site.register(CommentStationSite, CommentStationSiteAdmin)

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectUser, ProjectUserAdmin)
#admin.site.register(LoggedActions)
admin.site.register(ParameterEquip, ParameterEquipAdmin)
admin.site.register(ParameterValue, ParameterValueAdmin)
admin.site.register(ChannelCode, ChannelCodeAdmin)
#admin.site.register(ChainConfigTest)
