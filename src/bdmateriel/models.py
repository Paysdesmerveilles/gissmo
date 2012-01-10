# coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Ajout pour definir un lien entre des champs FK. Ce qui limitera le choix du drop down select d'un champ FK
from smart_selects.db_fields import ChainedForeignKey 
# Fin de l'ajout pour definir un lien entre des champs FK

# Ajout pour lever des erreurs de validation
from django.core.exceptions import ValidationError
# Fin de l'ajout pour lever des erreurs de validation

"""
####
#
# Actor's section
#
####
"""

"""We use this as a public class example class. 

You never call this class before calling :func:`public_fn_with_sphinxy_docstring`.

.. note::

An example of intersphinx is this: you **cannot** use :mod:`pickle` on this class.

"""

# Type of access to the actor
class AccessType(models.Model):
    access_type_name = models.CharField(max_length=40, verbose_name=_("type d'acces"))

    class Meta:
        ordering = ['access_type_name']
        verbose_name = _("type d'acces")
        verbose_name_plural = _("type d'acces")

    def __unicode__(self):
        return self.access_type_name

# Actor
class Actor(models.Model):
    actor_name = models.CharField(max_length=50, verbose_name=_("nom"))
    actor_note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("intervenant")
        verbose_name_plural = _("E1. Intervenants")

    def __unicode__(self):
        return self.actor_name

# Kind of accessibilty and coordinate to contact the actor
class ActorAccessibility(models.Model):
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    access_type = models.ForeignKey("AccessType", verbose_name=_("type d'acces"))
    coordinate = models.TextField(null=True, blank=True, verbose_name=_("coordonnees"))

    class Meta:
        verbose_name = _("accessbilite a l'intervenant")
        verbose_name_plural = _("D2. Accessibilite aux intervenants")

    def __unicode__(self):
      return u'%s %s %s' % (self.actor.actor_name, self.access_type.access_type_name, self.coordinate)

# Address of the actor
class ActorAddress(models.Model):
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("adresse"))
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("commune"))
    department = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("departement"))
    region = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("region"))
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("pays"))
    zip_code = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("code postal"))

    class Meta:
        ordering = ['actor']
        verbose_name = _("adresse de l'intervenant")
        verbose_name_plural = _("D3. Adresses des intervenants")

    def __unicode__(self):
      return u'%s %s' % (self.actor.actor_name, self.address)

# Role that an actor can have
class ActorType(models.Model):
    actor_type_name = models.CharField(max_length=40, verbose_name=_("type d'intervenant"))

    class Meta:
        ordering = ['actor_type_name']
        verbose_name = _("type d'intervenant")
        verbose_name_plural = _("types des intervenants")

    def __unicode__(self):
        return self.actor_type_name

####
#
# Built's section
#
####

# Category of the built
class BuiltCategory(models.Model):
    built_category_name = models.CharField(max_length=40, verbose_name=_("categorie du bati"))

    class Meta:
        ordering = ['built_category_name']
        verbose_name = _("categorie du bati")
        verbose_name_plural = _("categories des batis")

    def __unicode__(self):
        return self.built_category_name

# Type of the built
class BuiltType(models.Model):
    built_type_name = models.CharField(max_length=40, verbose_name=_("type de bati"))

    class Meta:
        ordering = ['built_type_name']
        verbose_name = _("type de bati")
        verbose_name_plural = _("types des batis")

    def __unicode__(self):
        return self.built_type_name

# Builts on the site of a station
class Built(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    built_category = models.ForeignKey("BuiltCategory", verbose_name=_("categorie du bati"))
    built_type = models.ForeignKey("BuiltType", verbose_name=_("type de bati"))
    built_note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("bati")
        verbose_name_plural = _("B1. Batis")

    def __unicode__(self):
        return u'%s %s %s' % (self.station.station_code, self.built_category.built_category_name, self.built_type.built_type_name)

####
#
# Equipment's section
#
####

# Type of action that occur on equipment
class EquipActionType(models.Model):
    equip_action_type = models.CharField(max_length=40, verbose_name=_("type d'action"))

    class Meta:
        ordering = ['equip_action_type']
        verbose_name = _("type d'action sur l'equipement")
        verbose_name_plural = _("types d'actions sur les equipements")

    def __unicode__(self):
        return self.equip_action_type

#
# Equipment's actors
#
class EquipActor(models.Model):
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    actor_type = models.ForeignKey("ActorType", verbose_name=_("role de l'intervenant"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("intervenant de l'equipement")
        verbose_name_plural = _("E3. Intervenants des equipements")

    def __unicode__(self):
        return u'%s %s %s' % (self.equip.equip_model.equip_model_name, self.actor.actor_name, self.actor_type.actor_type_name)

# Characteristics of an equipment
class EquipCharac(models.Model):
    equip_charac_name = models.CharField(max_length=50, verbose_name=_("caracteristique"))

    class Meta:
        verbose_name = _("caracteristique de l'equipement")
        verbose_name_plural = _("caracteristiques des equipements")

    def __unicode__(self):
        return self.equip_charac_name

# Possible values for the characteristics of an equipment
# pour l'instant aucun choix de valeur n'est disponible
#class EquipCharacValue(models.Model) :
#    equip_charac = models.ForeignKey("EquipCharac", verbose_name=_("Caracteristique"))
#    value_choice = models.CharField(max_length=50, verbose_name=_("Choix de valeur"))
#
#    class Meta:
#        ordering = ['id']
#        verbose_name = _("Choix de valeur de la caracteristique equipement")
#        verbose_name_plural = _("Choix de valeur des caracteristiques equipement")
#
#    def __unicode__(self):
#        return self.value_choice

# Supertype or category of equipment
class EquipSupertype(models.Model):
    equip_supertype_name = models.CharField(max_length=40, verbose_name=_("supertype d'equipement"))

    class Meta:
        ordering = ['equip_supertype_name']
        verbose_name = _("supertype de l'equipement")
        verbose_name_plural = _("supertypes des equipements")

    def __unicode__(self):
        return self.equip_supertype_name

## Type of equipment
class EquipType(models.Model):
    equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
    equip_type_name = models.CharField(max_length=40, verbose_name=_("type d'equipement"))

    class Meta:
        ordering = ['equip_supertype__equip_supertype_name','equip_type_name']
        verbose_name = _("type d'equipement")
        verbose_name_plural = _("types des equipements")

    def __unicode__(self):
        return self.equip_type_name

# Models of equipment
class EquipModel(models.Model):
    equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
    equip_type = ChainedForeignKey(
        EquipType,
        chained_field="equip_supertype",
        chained_model_field="equip_supertype", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("type d'equipement")
    )
    equip_model_name = models.CharField(max_length=50, verbose_name=_("modele d'equipement"))

    class Meta:
        verbose_name = _("modele d'equipement")
        verbose_name_plural = _("C1. Modeles des equipements")

    def __unicode__(self):
        return self.equip_model_name

# Equipments
class Equipment(models.Model):
    equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
    equip_type = ChainedForeignKey(
        EquipType,
        chained_field="equip_supertype",
        chained_model_field="equip_supertype", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("type d'equipement")
    )
    equip_model = ChainedForeignKey(
        EquipModel,
        chained_field="equip_type",
        chained_model_field="equip_type", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("modele d'equipement")
    )
    serial_number = models.CharField(max_length=50, verbose_name=_("numero de serie"))

    class Meta:
        verbose_name = _("equipement")
        verbose_name_plural = _("D1. Equipements")

    def __unicode__(self):
        return u'%s : %s' % (self.equip_model, self.serial_number)

# Possible state of an equipment
class EquipState(models.Model):
    equip_state_name = models.CharField(max_length=40, verbose_name=_("etat de l'equipement"))

    class Meta:
        ordering = ['equip_state_name']
        verbose_name = _("etat de l'equipement")
        verbose_name_plural = _("etats des equipements")

    def __unicode__(self):
        return self.equip_state_name

####
#
# Network's section
#
####

# Network
class Network(models.Model):
    network_code = models.CharField(max_length=5, verbose_name=_("code reseau"))
    network_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom du reseau"))
    main_network = models.ForeignKey('self', null=True, blank=True, verbose_name=_("reseau principal"))

    class Meta:
        verbose_name = _("reseau")
        verbose_name_plural = _("F1. Reseaux")

    def __unicode__(self):
        return self.network_code

####
#
# Station's section
#
####

# Type of action that occur on station
class StationActionType(models.Model):
    station_action_type = models.CharField(max_length=40, verbose_name=_("type d'action"))

    class Meta:
        ordering = ['station_action_type']
        verbose_name = _("type d'action sur la station")
        verbose_name_plural = _("types d'actions sur les stations")

    def __unicode__(self):
        return self.station_action_type

#
# Station's actors
#
class StationActor(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    actor_type = models.ForeignKey("ActorType", verbose_name=_("role"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("intervenant de la station")
        verbose_name_plural = _("E2. Intervenants des stations")

    def __unicode__(self):
        return u'%s : %s : %s' % (self.station.station_code, self.actor.actor_name, self.actor_type.actor_type_name)

# Characteristics of a station
class StationCharac(models.Model):
    station_charac_name = models.CharField(max_length=50, verbose_name=_("caracteristique"))

    class Meta:
        ordering = ['station_charac_name']
        verbose_name = _("caracteristique de la station")
        verbose_name_plural = _("caracteristiques des stations")

    def __unicode__(self):
        return self.station_charac_name

# Possible values for the characteristics of a station
class StationCharacValue(models.Model):
    station_charac = models.ForeignKey("StationCharac", verbose_name=_("caracteristique"))
    station_charac_value = models.CharField(max_length=50, verbose_name=_("choix de valeur"))

    class Meta:
        ordering = ['id']
        verbose_name = _("choix de valeur de la caract. station")
        verbose_name_plural = _("choix de valeur des caract. station")

    def __unicode__(self):
        return self.station_charac_value

# Station or site 
class StationSite(models.Model):
    station_code = models.CharField(max_length=40, verbose_name=_("code station"))
    station_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom station"))
    latitude = models.FloatField(null=True, blank=True, verbose_name=_("latitude"))
    longitude = models.FloatField(null=True, blank=True, verbose_name=_("longitude"))
    elevation = models.FloatField(null=True, blank=True, verbose_name=_("elevation"))
    site_name = models.CharField(null=True, blank=True,max_length=100, verbose_name=_("nom site"))
    site_description = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("description"))
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("adresse"))
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("commune"))
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("departement"))
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("region"))
    country =  models.CharField(max_length=50, null=True, blank=True, verbose_name=_("pays"))
    zip_code = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("code postal"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        ordering = ['station_code']
        verbose_name = _("station")
        verbose_name_plural = _("A1. Stations")

    def __unicode__(self):
        return self.station_code


# Possible state of a station
class StationState(models.Model):
    station_state_name = models.CharField(max_length=40, verbose_name=_("etat de la station"))

    class Meta:
        ordering = ['station_state_name']
        verbose_name = _("etat de la station")
        verbose_name_plural = _("etats des stations")

    def __unicode__(self):
        return self.station_state_name

####
#
# Historic's section
#
####
#
# Historic of the equipment's actions
#
class HistoricEquipAction(models.Model):
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    equip_action_type = models.ForeignKey("EquipActionType", verbose_name=_("action"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))
    station_action = models.ForeignKey("HistoricStationAction", null=True, blank=True, verbose_name=_("intervention station"))

    class Meta:
        verbose_name = _("hist. des actions sur l'equipement")
        verbose_name_plural = _("D3. Hist. des actions sur les equipements")

    def clean(self):
        """
        Makes sure the date of equipment action is the same as the station action if there is a relation establish
        """
        if not self.station_action == None:
            if not self.start_date == self.station_action.start_date:
                raise ValidationError('La date de l\'action sur l\'equipement ne correspond pas '
                                      ' avec celle de l\'action sur la station.')

    def __unicode__(self):
        return u'%s %s' % (self.equip.equip_model.equip_model_name, self.equip_action_type.equip_action_type)

# Historic of the equipment's characteristics
class HistoricEquipCharac(models.Model):
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    equip_charac = models.ForeignKey("EquipCharac", verbose_name=_("caracteristique"))
    equip_charac_value = models.TextField(null=True, blank=True, verbose_name=_("valeur"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("hist. des caract. de l'equipement")
        verbose_name_plural = _("D4. Hist. des caract. des equipements")

    def __unicode__(self):
        return u'%s %s %s' % (self.equip.equip_model.equip_model_name, self.equip_charac.equip_charac_name, self.equip_charac_value)

# Historic of the equipment's states
class HistoricEquipState(models.Model):
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    equip_state = models.ForeignKey("EquipState", verbose_name=_("etat"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("hist. des etats de l'equipement")
        verbose_name_plural = _("D2. Hist. des etats des equipements")

    def __unicode__(self):
        return u'%s %s' % (self.equip.equip_model, self.equip_state.equip_state_name)

# Historic of the station's actions
class HistoricStationAction(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    station_action_type = models.ForeignKey("StationActionType", verbose_name=_("action"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("Hist. des actions sur la station")
        verbose_name_plural = _("A3. Hist. des actions sur les stations")

    def __unicode__(self):
        return u'%s %s' % (self.station.station_code, self.station_action_type.station_action_type)

# Historic of the station's characteristics 
class HistoricStationCharac(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    station_charac = models.ForeignKey("StationCharac", verbose_name=_("caracteristique"))
    station_charac_value = ChainedForeignKey(
        StationCharacValue,
        chained_field="station_charac",
        chained_model_field="station_charac", 
        show_all=False, 
        auto_choose=True,
        verbose_name=_("valeur")
    )
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("hist. des caract. de la station")
        verbose_name_plural = _("A4. Hist. des caract. des stations")

    def __unicode__(self):
        return u'%s : %s : %s' % (self.station.station_code, self.station_charac.station_charac_name, self.station_charac_value.station_charac_value)

# Historic of the station's states
class HistoricStationState(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    station_state = models.ForeignKey("StationState", verbose_name=_("etat"))
    start_date = models.DateField(null=True,blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True,blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("hist. des etats de la station")
        verbose_name_plural = _("A2. Hist. des etats des stations")

    def __unicode__(self):
        return u'%s %s' % (self.station.station_code, self.station_state.station_state_name)

# Historic of the different equipments found on a station
class HistoricStationEquip(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
    equip_type = ChainedForeignKey(
        EquipType,
        chained_field="equip_supertype",
        chained_model_field="equip_supertype", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("type d'equipement")
    )
    equip = ChainedForeignKey(
        Equipment,
        chained_field="equip_type",
        chained_model_field="equip_type", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("equipement")
    )
    network = models.ForeignKey("Network", null=True, blank=True, verbose_name=_("reseau"))
    built = ChainedForeignKey(
        Built,
        chained_field="station",
        chained_model_field="station", 
        show_all=False, 
        auto_choose=False, 
        verbose_name=_("bati"),
        null=True, 
        blank=True
    )
    host_equipment = models.ForeignKey("Equipment", null=True, blank=True, verbose_name=_("equipement hote"), related_name='host')
    start_date = models.DateField(null=True, blank=True, verbose_name=_("date debut"))
    end_date = models.DateField(null=True, blank=True, verbose_name=_("date fin"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        ordering = ['start_date']
        verbose_name = _("hist. des equipements de la station")
        verbose_name_plural = _("A5. Hist. des equipements des stations")

    def __unicode__(self):
        return u'%s : %s' % (self.station.station_code, self.equip)

# Management of station document

#### def stationdoc_file_name(self, filename):
####         return 'stations/%s_%s/%s' % (self.station.id, self.station.station_code, filename)

#### class StationDoc(models.Model):
####     station = models.ForeignKey("StationSite", verbose_name=_("station"))
####     document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
####     inscription_date = models.DateField(verbose_name=_("date inscription"))
####     document_station = models.FileField(verbose_name=_("document"), upload_to=stationdoc_file_name)
#### 
####     class Meta:
####         unique_together = ("station", "document_title", "inscription_date")
####         verbose_name = _("Document de la station")
####         verbose_name_plural = _("G1. Documents des stations")
#### 
####     def __unicode__(self):
####         return u'%s %s %s' % (self.station.station_code, self.document_title, self.inscription_date)

# Management of equipment model document

#### def equipmodeldoc_file_name(self, filename):
####         return 'equipements/%s_%s/%s' % (self.equip_model.id, self.equip_model.equip_model_name, filename)

#### class EquipModelDoc(models.Model):
####     equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
####     equip_type = ChainedForeignKey(
####         EquipType,
####         chained_field="equip_supertype",
####         chained_model_field="equip_supertype", 
####         show_all=False, 
####         auto_choose=True, 
####         verbose_name=_("type d'equipement")
####     )
####     equip_model = ChainedForeignKey(
####         EquipModel,
####         chained_field="equip_type",
####         chained_model_field="equip_type", 
####         show_all=False, 
####         auto_choose=True, 
####         verbose_name=_("modele d'equipement")
####     )
####     document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
####     inscription_date = models.DateField(verbose_name=_("date inscription"))
####     document_equip_model = models.FileField(verbose_name=_("document"), upload_to=equipmodeldoc_file_name)
#### 
####     class Meta:
####         unique_together = ("equip_model", "document_title", "inscription_date")
####         verbose_name = _("Document du modele d'equipement")
####         verbose_name_plural = _("G2. Documents des modeles d'equipement")
#### 
####     def __unicode__(self):
####         return u'%s %s %s' % (self.equip_model.equip_model_name, self.document_title, self.inscription_date)

# Management of equipment document

#### def equipdoc_file_name(self, filename):
####         return 'equipements/%s_%s/%s_%s_%s/%s' % (self.equip.equip_model.id, self.equip.equip_model.equip_model_name, self.equip.id, self.equip.equip_model.equip_model_name, self.equip.serial_number, filename)

#### class EquipDoc(models.Model):
####     equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
####     equip_type = ChainedForeignKey(
####         EquipType,
####         chained_field="equip_supertype",
####         chained_model_field="equip_supertype", 
####         show_all=False, 
####         auto_choose=True, 
####         verbose_name=_("type d'equipement")
####     )
####     equip_model = ChainedForeignKey(
####         EquipModel,
####         chained_field="equip_type",
####         chained_model_field="equip_type", 
####         show_all=False, 
####         auto_choose=True, 
####         verbose_name=_("modele d'equipement")
####     )
####     equip = ChainedForeignKey(
####         Equipment,
####         chained_field="equip_model",
####         chained_model_field="equip_model", 
####         show_all=False, 
####         auto_choose=True, 
####         verbose_name=_("equipement")
####     )
####     document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
####     inscription_date = models.DateField(verbose_name=_("date inscription"))
####     document_equip = models.FileField(verbose_name=_("document"), upload_to=equipdoc_file_name)
#### 
####     class Meta:
####         unique_together = ("equip", "document_title", "inscription_date")
####         verbose_name = _("Document de l'equipement")
####         verbose_name_plural = _("G3. Documents des equipements")
#### 
####     def __unicode__(self):
####         return u'%s %s %s %s' % (self.equip.equip_model.equip_model_name, self.equip.serial_number, self.document_title, self.inscription_date)

# Acquisition chain

#### class AcquisitionChain(models.Model) :
####     station = models.ForeignKey("StationSite", verbose_name=_("station"))
####     location_code = models.CharField(max_length=2, verbose_name=_("code localisation"))
####     latitude = models.FloatField(null=True, blank=True, verbose_name=_("latitude"))
####     longitude = models.FloatField(null=True, blank=True, verbose_name=_("longitude"))
####     elevation = models.FloatField(null=True, blank=True, verbose_name=_("elevation"))
####     depth = models.FloatField(null=True, blank=True, verbose_name=_("profondeur"))
#### 
####     class Meta:
####         verbose_name = _("Chaine d'acquisition")
####         verbose_name_plural = _("H1. Chaines d'acquisition")
####     
####     def __unicode__(self):
####         return u'%s : %s' % (self.station.station_code, self.location_code)

#### class ChainComponent(models.Model) :
####     acquisition_chain = models.ForeignKey('AcquisitionChain', verbose_name=_("chaine d'acquisition"))
####     equip = models.ForeignKey('Equipment', verbose_name=_("equipement"))
####     order = models.IntegerField(null=True, blank=True, verbose_name=_("ordre"))
####     start_date = models.DateField(verbose_name=_("date debut"))
####     end_date = models.DateField(null=True, blank=True, verbose_name=_("date fin"))
#### 
####     class Meta:
####         verbose_name = _("Composante de la chaine d'acqui")
####         verbose_name_plural = _("H2. Composantes des chaines d'acqui")

##    def clean(self):
##        """
##        Makes sure the equipment is in the station
##        """
##        if any(self.errors):
##            # Don't bother validating the formset unless each form is valid on its own
##            return
###        print self
##        if not self.acquisition_chain == None:
#            print self.acquisition_chain
#            print self.order
#            print self.end_date
#            if not self.equip == None:
#                print self.equip
##            L = [equip.equip_id for equip in HistoricStationEquip.objects.filter(station=self.acquisition_chain.station.id)]
#            print L
#            if not self.equip == None:
#                print self.equip
#                if not self.equip.id == None and self.equip.id not in L:
##            if self.equip.id not in L:
##                    raise ValidationError('L\'equipment inscrit n\'est pas installe dans la station.')

####     def __unicode__(self):
####         return u'%s : %s : %s : %s : %s' % (self.acquisition_chain, self.equip.equip_model.equip_model_name, self.equip.serial_number, self.start_date, self.end_date)

#### class Channel(models.Model) :
####     network = models.ForeignKey('Network', verbose_name=_("reseau"))
####     acquisition_chain = models.ForeignKey('AcquisitionChain', verbose_name=_("chaine d'acquisition"))
####     channel_code = models.CharField(max_length=3, verbose_name=_("code du canal"))
####     dip = models.FloatField(null=True, blank=True, max_length=5, verbose_name=_("angle d'inclinaison"))
####     azimuth = models.FloatField(null=True, blank=True, max_length=5, verbose_name=_("azimut"))
####     sample_rate =  models.FloatField(verbose_name=_("frequence (Hz)"))
####     start_date = models.DateField(verbose_name=_("date debut"))
####     end_date = models.DateField(null=True, blank=True, verbose_name=_("date fin"))
#### 
####     class Meta:
####         verbose_name = _("Canal d'acquisition")
####         verbose_name_plural = _("H3. Canaux d'acquisition")
#### 
####     def __unicode__(self):
####         return u'%s : %s : %s : %s' % (self.network, self.acquisition_chain, self.channel_code, self.sample_rate)
