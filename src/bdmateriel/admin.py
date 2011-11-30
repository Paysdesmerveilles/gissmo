from models import *
from django.contrib import admin

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
from django.http import Http404, HttpResponse, HttpResponseRedirect

"""
Usage:

SubmitButtonField(label="", initial=u"Your submit button text")
"""

#from django import forms
#from django.utils import html

#class ButtonWidget(forms.Widget):
#    def render(self, name, value, attrs=None):
#        return mark_safe('<input type="button" name="%s" value="%s" onclick="self.location.href=\'http://www.google.com\'">' % (html.escape(name), html.escape(value)))

#class ButtonField(forms.Field):
#    def __init__(self, *args, **kwargs):
#        kwargs["widget"] = ButtonWidget
#
#        super(ButtonField, self).__init__(*args, **kwargs)
#
#    def clean(self, value):
#        return value

#class SubmitButtonWidget(forms.Widget):
#    def render(self, name, value, attrs=None):
#        return mark_safe('<input type="submit" name="%s" value="%s">' % (html.escape(name), html.escape(value)))

#class SubmitButtonField(forms.Field):
#    def __init__(self, *args, **kwargs):
#        if not kwargs:
#            kwargs = {}
#        kwargs["widget"] = SubmitButtonWidget
#
#        super(SubmitButtonField, self).__init__(*args, **kwargs)
#
#    def clean(self, value):
#        return value

# Ajout pour URLField admin widget with View Link button
#from django.contrib.admin.widgets import AdminURLFieldWidget
#from django.db.models import URLField
#from django.utils.safestring import mark_safe

#class URLFieldWidget(AdminURLFieldWidget):
#    def render(self, name, value, attrs=None):
#        widget = super(URLFieldWidget, self).render(name, value, attrs)
#        return mark_safe(u'%s&nbsp;&nbsp;<input type="button" '
#                         u'value="Aller au lien" onclick="window.'
#                         u'open(document.getElementById(\'%s\')'
#                         u'.value)" />' % (widget, attrs['id']))

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

class ActorAccessibilityInline(admin.TabularInline):
    model = ActorAccessibility
    extra = 0

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class ActorAddressInline(admin.TabularInline):
    model = ActorAddress
    extra = 0

class ActorAdmin(admin.ModelAdmin):
    ordering = ['actor_name']
    search_fields = ['actor_name']

    inlines = [ActorAccessibilityInline, ActorAddressInline,]    

####
#
# ActorAddressAdmin's section
#
####

class ActorAddressAdmin(admin.ModelAdmin):
    list_display = ['actor', 'address', 'city', 'department', 'region', 'country', 'zip_code',]
    ordering = ['actor__actor_name']

####
#
# BuiltAdmin's section
#
####

class BuiltAdmin(admin.ModelAdmin):
    list_display = ['station', 'built_category', 'built_type',]
    ordering = ['station']
    search_fields = ['station__station_code']

    special_ordering = {'station': ('station__station_code', 'built_category__built_category_name', 'built_type__built_type_name'), 'built_category': ('built_category__built_category_name', 'built_type__built_type_name')}
 
    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

####
#
# EquipmentAdmin's section
#
####

class EquipActorAdmin(admin.ModelAdmin):
    list_display = ['equip', 'actor', 'actor_type', 'start_date', 'end_date',]
    ordering = ['equip']
    search_fields = ['equip__equip_model__equip_model_name', 'equip__serial_number', 'actor__actor_name']

class EquipModelAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model_name',]
    list_filter = ['equip_supertype', 'equip_type',]
    search_fields = ['equip_model_name']

    fieldsets = [('', {'fields': [('equip_supertype', 'equip_type', 'equip_model_name')]}),]

class EquipActorInline(admin.TabularInline):
    model = EquipActor
    extra = 0

    # Presenter les champs dans l'ordre ci-dessous au lieu de : 'actor_type', 'actor', 'start_date', 'end_date', 'note' comme definit dans le modele
    fields = ('actor', 'actor_type', 'start_date', 'end_date', 'note')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

#class HistoricEquipActionInlineFormset(forms.models.BaseInlineFormSet):
# 
#    def add_fields(self, form, index):
#        super(HistoricEquipActionInlineFormset, self).add_fields(form, index)
#        form.fields['start_date'].initial = '2011-02-02'
#        form.fields['note'].initial = 'Test'
             
class HistoricEquipActionInline(admin.TabularInline):
    model = HistoricEquipAction
#    formset = HistoricEquipActionInlineFormset
    extra = 0

#    def get_formset(self, request, obj=None, **kwargs):
#        # Hack! Hook parent obj just in time to use in formfield_for_manytomany
#        self.parent_obj = obj
#        print self.parent_obj
#        return super(HistoricEquipActionInline, self).get_formset(
#            request, obj, **kwargs)
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class HistoricEquipCharacInline(admin.TabularInline):
    model = HistoricEquipCharac
    extra = 0
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class HistoricEquipStateInline(admin.TabularInline):
    model = HistoricEquipState
    extra = 0
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class HistoricEquipStationInlineFormset(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(HistoricEquipStationInlineFormset, self).add_fields(form, index)
        builts = Built.objects.none()
        host_equipments = HistoricStationEquip.objects.none()
        if form.instance:
            try :
                station = form.instance.station
            except StationSite.DoesNotExist:
                pass
            else :
                builts = Built.objects.filter(station=station.pk)
                host_equipments = HistoricStationEquip.objects.filter(station=station.pk)
        form.fields['built'].queryset = builts
        form.fields['host_equipment'].queryset = host_equipments

class HistoricEquipStationInline(admin.TabularInline):
    model = HistoricStationEquip
    fk_name = 'equip'
    formset = HistoricEquipStationInlineFormset
    extra = 1
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type', 'equip_model', 'serial_number',]
    list_filter = ['equip_supertype', 'equip_type', 'equip_model',]
    ordering = ['equip_supertype']
    search_fields = ['equip_model__equip_model_name', 'serial_number']

    special_ordering = {'equip_supertype': ('equip_supertype__equip_supertype_name', 'equip_type__equip_type_name', 'equip_model__equip_model_name','serial_number'), 'equip_type': ('equip_type__equip_type_name', 'equip_model__equip_model_name','serial_number'), 'equip_model': ('equip_model__equip_model_name','serial_number')}
 
    fieldsets = [('', {'fields': [('equip_supertype', 'equip_type', 'equip_model', 'serial_number')]}),]

    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

    inlines = [EquipActorInline, HistoricEquipStateInline, HistoricEquipActionInline, HistoricEquipCharacInline, HistoricEquipStationInline]

####
#
# StationAdmin's section
#
####

class StationActorAdmin(admin.ModelAdmin):
    list_display = ['station', 'actor', 'actor_type', 'start_date', 'end_date',]
    ordering = ['station']
    search_fields = ['station__station_code', 'actor__actor_name']

class StationActorInline(admin.TabularInline):
    model = StationActor
    extra = 0

    # ordering difffently the field 
    fields = ('actor', 'actor_type', 'start_date', 'end_date', 'note')

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

#class HistoricStationActionForm(forms.ModelForm):
#    bouton = ButtonField(label="Bouton", initial=u"Action equipement", widget=ButtonWidget)
#    my_url = forms.CharField(widget=URLFieldWidget)
#    class Meta:
#        model = HistoricStationAction

class HistoricStationActionInline(admin.TabularInline):
    model = HistoricStationAction
    extra = 0
    ordering = ['-start_date']
    template = 'admin/HistoricStationAction.html'
    admin_model_path = None

    def __init__(self, *args):
        super(HistoricStationActionInline, self).__init__(*args)
        if self.admin_model_path is None:
            self.admin_model_path = self.model.__name__.lower()

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':3})},
    }

class HistoricStationCharacInline(admin.TabularInline):
    model = HistoricStationCharac
    extra = 1
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class HistoricStationStateInline(admin.TabularInline):
    model = HistoricStationState
    extra = 0
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class BuiltInline(admin.TabularInline):
    model = Built
    extra = 0
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class HistoricStationEquipInline(admin.TabularInline):
    model = HistoricStationEquip
    extra = 1
 
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

    ####
    #
    # Pour limiter dans le choix du select de la FK
    # que les batis et les equipements de la station
    #
    ####

    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'host_equipment':
            parent_station = self.get_object(kwargs['request'], StationSite)
            L = [equip.equip_id for equip in HistoricStationEquip.objects.filter(station=parent_station)]
            contained_equip = Equipment.objects.filter(id__in = L)
            return forms.ModelChoiceField(label="Equipement hote",queryset=contained_equip,required=False)
        return super(HistoricStationEquipInline, self).formfield_for_dbfield(field, **kwargs)

    def get_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return model.objects.get(pk=object_id)

class StationSiteAdmin(admin.ModelAdmin):
    list_display = ('station_code', 'station_name', 'site_name','latitude','longitude','elevation')
    ordering = ['station_code']
    search_fields = ['station_code']

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }
    fieldsets = [
        ('Information sur la station' , {'fields': [('station_code','station_name','latitude','longitude','elevation')]}),
        ('Information sur le site' , {'fields': [('site_name','site_description','note'),('address', 'zip_code', 'city'),('department','region','country')], 'classes': ['collapse']}),
    ]
    inlines = [StationActorInline, HistoricStationStateInline, HistoricStationActionInline, HistoricStationCharacInline, BuiltInline, HistoricStationEquipInline]

####
#
# HistoricAdmin's section
#
####

class HistoricEquipActionAdmin(admin.ModelAdmin):
    list_display = ['equip', 'equip_action_type', 'start_date',]
    list_filter = ['equip_action_type',]
    search_fields = ['equip__equip_model__equip_model_name', 'equip__serial_number']

class HistoricEquipCharacAdmin(admin.ModelAdmin):
    list_display = ['equip', 'equip_charac', 'equip_charac_value', 'start_date', 'end_date',]

class HistoricEquipStateAdmin(admin.ModelAdmin):
    list_display = ['equip', 'equip_state', 'start_date', 'end_date',]
    list_filter = ['equip_state',]
    search_fields = ['equip__equip_model__equip_model_name', 'equip__serial_number']

class HistoricStationActionAdmin(admin.ModelAdmin):
    list_display = ['station', 'station_action_type', 'start_date', ]
    list_filter = ['station_action_type',]
    ordering = ['station']
    search_fields = ['station__station_code']

    inlines = [HistoricEquipActionInline] 

    special_ordering = {'station': ('station__station_code', 'station_action_type__station_action_type', 'start_date'), 'station_action': ('station_action_type__station_action_type', 'start_date')}
 
    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = obj._meta

        # Handle proxy models automatically created by .only() or .defer()
        verbose_name = opts.verbose_name
        if obj._deferred:
            opts_ = opts.proxy_for_model._meta
            verbose_name = opts_.verbose_name

        pk_value = obj._get_pk_val()

        msg = _('The %(name)s "%(obj)s" was changedt successfully.') % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}
        if "_popup" in request.POST:
            return HttpResponse('<script type="text/javascript">window.close();</script>')
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        elif "_saveasnew" in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % {'name': force_unicode(verbose_name), 'obj': obj}
            self.message_user(request, msg)
            return HttpResponseRedirect("../%s/" % pk_value)
        elif "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(verbose_name)))
            return HttpResponseRedirect("../add/")
        else:
            self.message_user(request, msg)
            # Figure out where to redirect. If the user has change permission,
            # redirect to the change-list page for this object. Otherwise,
            # redirect to the admin index.
            if self.has_change_permission(request, None):
                return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../../../')

class HistoricStationCharacAdmin(admin.ModelAdmin):
    list_display = ['station', 'station_charac', 'station_charac_value', 'start_date', 'end_date', 'note']
    list_filter = ['station_charac', 'station_charac_value',]
    ordering = ['station']
    search_fields = ['station__station_code']

    special_ordering = {'station': ('station__station_code', 'station_charac__station_charac_name', 'start_date'), 'station_charac': ('station_charac__station_charac_name', 'start_date')}
 
    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

class HistoricStationStateAdmin(admin.ModelAdmin):
    list_display = ['station', 'station_state', 'start_date', 'end_date',]
    list_filter = ['station_state',]
    ordering = ['station']
    search_fields = ['station__station_code']

    special_ordering = {'station': ('station__station_code', 'station_state__station_state_name', 'start_date'), 'station_state': ('station_state__station_state_name', 'start_date')}
 
    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

class HistoricStationEquipForm(forms.ModelForm):

    class Meta:
        model = HistoricStationEquip

    def __init__(self, *args, **kwargs):
        super(HistoricStationEquipForm, self).__init__(*args, **kwargs)
        if 'instance' in kwargs:
            historique = kwargs['instance']
            parent_station = historique.station_id
            L = [equip.equip_id for equip in HistoricStationEquip.objects.filter(station=parent_station)]
#            self.fields['built'].queryset = Built.objects.filter(station=parent_station)
            self.fields['host_equipment'].queryset = Equipment.objects.filter(id__in = L)
        else:
#            self.fields['built'].queryset = Built.objects.none()
            self.fields['host_equipment'].queryset = Equipment.objects.none()

class HistoricStationEquipAdmin(admin.ModelAdmin):
    form = HistoricStationEquipForm
    list_display = ['station', 'equip_supertype', 'equip_type', 'equip','network',]
    list_filter = ['equip_supertype', 'equip_type', 'network',]
    ordering = ['station']
    search_fields = ['station__station_code', 'equip__equip_model__equip_model_name', 'equip__serial_number']

    special_ordering = {'station': ('station__station_code', 'equip_supertype__equip_supertype_name', 'equip_type__equip_type_name', 'equip'), 'equip_supertype': ('equip_supertype__equip_supertype_name', 'equip_type__equip_type_name', 'equip'), 'equip_type': ('equip_type__equip_type_name', 'equip')}

    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

####
#
# Table code Admin's section
#
####

class EquipTypeAdmin(admin.ModelAdmin):
    list_display = ['equip_supertype', 'equip_type_name',]
    list_filter = ['equip_supertype',]

class NetworkAdmin(admin.ModelAdmin):

    def response_change(self, request, obj):
        """
        Determines the HttpResponse for the change_view stage.
        """
        opts = obj._meta

        # Handle proxy models automatically created by .only() or .defer()
        verbose_name = opts.verbose_name
        if obj._deferred:
            opts_ = opts.proxy_for_model._meta
            verbose_name = opts_.verbose_name

        pk_value = obj._get_pk_val()

        msg = _('The %(name)s "%(obj)s" was changedt successfully.') % {'name': force_unicode(verbose_name), 'obj': force_unicode(obj)}
        if "_popup" in request.POST:
            return HttpResponse('<script type="text/javascript">window.close();</script>')
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.REQUEST:
                return HttpResponseRedirect(request.path + "?_popup=1")
            else:
                return HttpResponseRedirect(request.path)
        elif "_saveasnew" in request.POST:
            msg = _('The %(name)s "%(obj)s" was added successfully. You may edit it again below.') % {'name': force_unicode(verbose_name), 'obj': obj}
            self.message_user(request, msg)
            return HttpResponseRedirect("../%s/" % pk_value)
        elif "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(verbose_name)))
            return HttpResponseRedirect("../add/")
        else:
            self.message_user(request, msg)
            # Figure out where to redirect. If the user has change permission,
            # redirect to the change-list page for this object. Otherwise,
            # redirect to the admin index.
            if self.has_change_permission(request, None):
                return HttpResponseRedirect('../')
            else:
                return HttpResponseRedirect('../../../')

#admin.site.register(AccessType)

admin.site.register(Actor, ActorAdmin)
#admin.site.register(ActorAccessibility)
#admin.site.register(ActorAddress, ActorAddressAdmin)
#admin.site.register(ActorType)

admin.site.register(Built, BuiltAdmin)
#admin.site.register(BuiltCategory)
#admin.site.register(BuiltType)

#admin.site.register(EquipActionType)
admin.site.register(EquipActor, EquipActorAdmin)
#admin.site.register(EquipCharac)
#admin.site.register(EquipCharacValue)
#admin.site.register(EquipSupertype)
#admin.site.register(EquipType,EquipTypeAdmin)
admin.site.register(EquipModel, EquipModelAdmin)
admin.site.register(Equipment, EquipmentAdmin)
#admin.site.register(EquipState)

admin.site.register(HistoricEquipAction, HistoricEquipActionAdmin)
admin.site.register(HistoricEquipCharac, HistoricEquipCharacAdmin)
admin.site.register(HistoricEquipState, HistoricEquipStateAdmin)
admin.site.register(HistoricStationAction, HistoricStationActionAdmin)
admin.site.register(HistoricStationCharac, HistoricStationCharacAdmin)
admin.site.register(HistoricStationState, HistoricStationStateAdmin)

admin.site.register(HistoricStationEquip, HistoricStationEquipAdmin)

admin.site.register(Network, NetworkAdmin)

#admin.site.register(StationActionType)
admin.site.register(StationActor, StationActorAdmin)
#admin.site.register(StationCharac)
#admin.site.register(StationCharacValue)
admin.site.register(StationSite, StationSiteAdmin)
#admin.site.register(StationState)




