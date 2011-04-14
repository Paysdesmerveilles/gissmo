from models import *
from django.contrib import admin

import os

# Ajout pour definir un autre formfield_for_dbfield
# afin de limiter le choix du select d'un champ FK
from django import forms
# Fin de l'ajout pour definir un autre formfield_for_dbfield

from django.forms import Textarea

# Ajout pour ordering by multiple fields in a column sort
from django.contrib.admin.views.main import ChangeList
# Fin de l'ajout pour ordering by multiple fields in a column sort

# Ajout pour URLField admin widget with View Link button
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField
from django.utils.safestring import mark_safe

class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<input type="button" '
                         u'value="Aller au lien" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value)" />' % (widget, attrs['id']))


# Inscrire formfield_overrides pour les champs URLFIELD
# pour lesquels on veut cette option aussi bien pour
# les Inline que l'Admin d'une classe
#
#    formfield_overrides = {
#        URLField: {'widget': URLFieldWidget},
#    }
#
# Fin de l'ajout pour URLField admin widget with View Link button

# Ajout pour ordering by multiple fields in a column sort
class SpecialOrderingChangeList(ChangeList):
    def apply_special_ordering(self, queryset):
        order_type, order_by = [self.params.get(param, None) for param in ('ot', 'o')]

        ordering_attr = self.model_admin.ordering or self.model._meta.ordering

        if order_type is None and order_by is None and ordering_attr is not None:
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

# Ajouter a l'admin de la classe qui comportera un tri sur champ multiple (voir EquipAdmin)
#
#    special_ordering
#
#    def get_changelist(self, request, **kwargs):
#        return SpecialOrderingChangeList
#
# pour lesquels on veut cette option
# Fin de l'ajout pour ordering by multiple fields in a column sort

class HistoriqueStationSiteInline(admin.TabularInline):
    model = HistoriqueStationSite
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class StationSiteIntervenantInline(admin.TabularInline):
    model = StationSiteIntervenant
    extra = 0

class BatiInline(admin.TabularInline):
    model = Bati
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    extra = 0
    #template = 'admin/tabular.html'

class EquipStationSiteInline(admin.TabularInline):
    model = EquipStationSite
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

# Pour limiter dans le choix du select de la FK
# que les batis et les equipements de la station
#
    def formfield_for_dbfield(self, field, **kwargs):
        if field.name == 'bati':
#            # Note - get_object hasn't been defined yet
            parent_station = self.get_object(kwargs['request'], StationSite)
            contained_batis = Bati.objects.filter(station=parent_station)
            return forms.ModelChoiceField(label="Bati",queryset=contained_batis,required=False)
        else :
            if field.name == 'equipement_hote':
                parent_station = self.get_object(kwargs['request'], StationSite)
                L = [equip.equipement_id for equip in EquipStationSite.objects.filter(station=parent_station)]
                contained_equip = Equipement.objects.filter(id__in = L)
                return forms.ModelChoiceField(label="Equipement hote",queryset=contained_equip,required=False)
        return super(EquipStationSiteInline, self).formfield_for_dbfield(field, **kwargs)

    def get_object(self, request, model):
        object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
        try:
            object_id = int(object_id)
        except ValueError:
            return None
        return model.objects.get(pk=object_id)

from django.forms.widgets import FileInput

#class AdminImageFieldWithThumbWidget(FileInput):
#
#    def __init__(self, thumb_width=50, thumb_height=50):
#        self.width = thumb_width
#        self.height = thumb_height
#        super(AdminImageFieldWithThumbWidget, self).__init__({})
#
#    def render(self, name, value, attrs=None):
#        thumb_html = ''
#        if value and hasattr(value, "url"):
#            thumb_html = '<img src="%s" width="%s" width="%s"/>' % (value.url, self.width, self.height)
#        return mark_safe("%s %s" % (super(AdminImageFieldWithThumbWidget, self).render(name, value,attrs), thumb_html))

class StationSiteAdmin(admin.ModelAdmin):
    list_display = ('code_station', 'nom_station', 'nom_site','latitude','longitude','elevation')

    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    fieldsets = [
        ('Information sur station et site' , {'fields': [('code_station','nom_station','classification','photo'),('latitude','longitude','elevation'),('nom_site','description')]}),
        ('Information sur le site' , {'fields': [('adresse','commune','pays','code_postal'),'geologie','googlemap','lien_documentation'], 'classes': ['collapse']}),

    ]
    inlines = [HistoriqueStationSiteInline, StationSiteIntervenantInline, BatiInline, EquipStationSiteInline]

#    def save_form(self, request, form, change):
#        """Deletes the file from fields FileField/ImageField if
#        their values have changed"""
#
#        obj = form.instance
#        if obj:
#            for field in obj._meta.fields:
#                if not isinstance(field, models.FileField):
#                    continue
#
#                path = getattr(obj, field.name, None)
#                if path and os.path.isfile(path.path):
#                    if field.name in form.changed_data or form.data.get('clear_image_'+field.name, ''):
#                        os.unlink(path.path)
#                        setattr(obj, field.name, None)
#
#        return super(StationSiteAdmin, self).save_form(request, form, change)
#
#    thumb_width = 100
#    thumb_height = 75
#    def formfield_for_dbfield(self, db_field, **kwargs):
#        field = super(StationSiteAdmin,self).formfield_for_dbfield(db_field,**kwargs)
#        if db_field.name == 'photo':
#            return forms.ImageField(widget=AdminImageFieldWithThumbWidget(thumb_width=self.thumb_width, thumb_height=self.thumb_height), required=False)
#        return field

class BatiAdmin(admin.ModelAdmin):
    list_display = ('station', 'description', 'categorie')
    list_filter = ['station','categorie']
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    fieldsets = [
        ('Information sur le bati' ,               {'fields': ['station','description','categorie','lien_documentation']}),
    ]

class AdresseInline(admin.TabularInline):
    model = Adresse
    extra = 0

class IntervenantAdmin(admin.ModelAdmin):
    list_display = ('categorie','nom','prenom','filiale','telephone','portable','fax','email')
    list_filter = ['categorie']
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    fieldsets = [
        ('Information sur l''intervenant' ,               {'fields': ['categorie','nom','prenom','filiale','telephone','portable','fax','email']}),
        ('Autre information', {'fields': ['note','lien_site'], 'classes': ['collapse']}),
    ]
    inlines = [AdresseInline]

class HistoriqueEquipInline(admin.TabularInline):
    model = HistoriqueEquip
    extra = 0
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class EquipSSiteInlineFormset(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(EquipSSiteInlineFormset, self).add_fields(form, index)
        batis = Bati.objects.none()
        if form.instance:
            try :
                station = form.instance.station
            except StationSite.DoesNotExist:
                pass
            else :
                batis = Bati.objects.filter(station=station.pk)
        form.fields['bati'].queryset = batis

class EquipSSiteInline(admin.TabularInline):
    model = EquipStationSite
    fk_name = 'equipement'
    extra = 0
    formset = EquipSSiteInlineFormset
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class EquipIntervenantInline(admin.TabularInline):
    model = EquipIntervenant
    extra = 0
    #template = 'admin/tabular.html'
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows':1})},
    }

class EquipAdmin(admin.ModelAdmin):
    list_display = ('super_categorie', 'categorie','constructeur', 'fournisseur', 'modele','no_serie')
    list_filter = ['super_categorie', 'categorie']

    special_ordering = {'super_categorie': ('super_categorie__nom', 'categorie__nom', 'constructeur__nom','fournisseur__nom','modele','no_serie'), 'categorie': ('categorie__nom', 'constructeur__nom','fournisseur__nom','modele','no_serie'), 'constructeur': ('constructeur__nom','fournisseur__nom','modele','no_serie'), 'fournisseur': ('fournisseur__nom','modele','no_serie')}

    def get_changelist(self, request, **kwargs):
        return SpecialOrderingChangeList

    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
    }
    fieldsets = [
        ('Information sur equipement' ,               {'fields': [('super_categorie','categorie','photo'),('constructeur','fournisseur'),('modele','no_serie')]}),
        ('Autre information', {'fields': [('dimension','poids'),'note','lien_documentation'], 'classes': ['collapse']}),
    ]
    inlines = [HistoriqueEquipInline, EquipSSiteInline, EquipIntervenantInline]

#    def save_form(self, request, form, change):
#        """Deletes the file from fields FileField/ImageField if
#        their values have changed"""
#
#        obj = form.instance
#        if obj:
#            for field in obj._meta.fields:
#                if not isinstance(field, models.FileField):
#                    continue
#
#                path = getattr(obj, field.name, None)
#                if path and os.path.isfile(path.path):
#                    if field.name in form.changed_data or form.data.get('clear_image_'+field.name, ''):
#                        os.unlink(path.path)
#                        setattr(obj, field.name, None)
#
#        return super(EquipAdmin, self).save_form(request, form, change)
#
#    thumb_width = 100
#    thumb_height = 75
#    def formfield_for_dbfield(self, db_field, **kwargs):
#        field = super(EquipAdmin,self).formfield_for_dbfield(db_field,**kwargs)
#        if db_field.name == 'photo':
#            return forms.ImageField(widget=AdminImageFieldWithThumbWidget(thumb_width=self.thumb_width, thumb_height=self.thumb_height), required=False)
#        return field

class HistoriqueEquipAdmin(admin.ModelAdmin):
    list_display = ('equipement', 'evenement','etat', 'date_debut', 'date_fin','note')
    list_filter = ['equipement', 'evenement','etat', 'date_debut', 'date_fin']

class HistoriqueStationSiteAdmin(admin.ModelAdmin):
    list_display = ('station', 'evenement','etat', 'date_debut', 'date_fin','note')
    list_filter = ['station', 'evenement','etat', 'date_debut', 'date_fin']

#admin.site.register(Classification)
admin.site.register(StationSite,StationSiteAdmin)
admin.site.register(Bati,BatiAdmin)

admin.site.register(Geologie)

#admin.site.register(CategorieBati)

admin.site.register(SuperCategorieEquip)
admin.site.register(CategorieEquip)

#admin.site.register(CategorieInterv)

admin.site.register(Reseau)

#admin.site.register(EvenementStation)

#admin.site.register(EvenementEquip)

admin.site.register(Intervenant,IntervenantAdmin)

#admin.site.register(Adresse)


admin.site.register(StationSiteIntervenant)


admin.site.register(Equipement,EquipAdmin)

admin.site.register(EquipIntervenant)

#admin.site.register(EquipStationSite)

admin.site.register(HistoriqueStationSite,HistoriqueStationSiteAdmin)

admin.site.register(HistoriqueEquip,HistoriqueEquipAdmin)


