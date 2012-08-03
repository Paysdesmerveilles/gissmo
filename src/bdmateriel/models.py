# coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Ajout pour definir un lien entre des champs FK. Ce qui limitera le choix du drop down select d'un champ FK
from smart_selects.db_fields import ChainedForeignKey 
# Fin de l'ajout pour definir un lien entre des champs FK

# Ajout pour lever des erreurs de validation
from django.core.exceptions import ValidationError
# Fin de l'ajout pour lever des erreurs de validation

from django.core.files.storage import FileSystemStorage
from django.conf import settings

fs = FileSystemStorage(location=settings.UPLOAD_ROOT)

# Ajout pour securiser les fichiers uploader
from django.contrib.auth.models import User
#from private_files import PrivateFileField
# Fin de l'ajout pour securiser les fichiers uploader
"""
####
#
# Actor's section
#
####
"""
# Actor
class Actor(models.Model):
    """
    Actor is the person who make the intervention
    
    Observatoire : OSU
    Instrumentaliste : Personne qui effectue une action sur une station
    Organisme :
    Entreprise : Unite economique de production de biens ou de services a but commercial
    Entreprise SAV : Unite economique de production de biens ou de services a but commercial qui est opérateur d'un site de type SAV
    Inconnu : 
    Autre :     
    """

    OBSERVATOIRE = 1
    INSTRUMENTALISTE = 2
    ORGANISME = 3
    ENTREPRISE = 4
    ENTREPRISE_SAV = 5
    INCONNU = 6
    AUTRE = 7
    ACTOR_TYPE_CHOICES = (
        (OBSERVATOIRE, 'Observatoire'),
        (INSTRUMENTALISTE, 'Instrumentaliste'),
        (ORGANISME, 'Organisme'),
        (ENTREPRISE, 'Entreprise'),
        (ENTREPRISE_SAV, 'Entreprise SAV'),
        (INCONNU, 'Inconnu'),
        (AUTRE, 'Autre'),
    ) 
    actor_type = models.IntegerField(choices=ACTOR_TYPE_CHOICES, default=AUTRE, verbose_name=_("Type d\'intervenant"))
    actor_name = models.CharField(max_length=50, unique=True, verbose_name=_("nom"))
    actor_note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name = _("intervenant")
        verbose_name_plural = _("E1. Intervenants")

    def __unicode__(self):
        return self.actor_name

####
#
# Built's section
#
####
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
    """
    Built on site that contain at least an equipment
    """
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    built_type = models.ForeignKey("BuiltType", verbose_name=_("type de bati"))
    built_short_desc =  models.CharField(max_length=40, null=True, blank=True, verbose_name=_("courte description"))
    built_note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        unique_together = ("station", "built_type", "built_short_desc")
        verbose_name = _("bati")
        verbose_name_plural = _("B1. Batis")

    def __unicode__(self):
        return u'%s : %s : %s' % (self.station.station_code, self.built_type.built_type_name, self.built_short_desc)

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

def get_defaut_owner():
    return Actor.objects.get(actor_name='DT INSU')

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
    owner = models.ForeignKey("Actor", default=get_defaut_owner, verbose_name=_("proprietaire"))
    contact = models.TextField(null=True, blank=True, verbose_name=_("contact"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))
   
    class Meta:
        unique_together = ("equip_supertype", "equip_type", "equip_model", "serial_number")
        verbose_name = _("equipement")
        verbose_name_plural = _("D1. Equipements")

    def __unicode__(self):
        return u'%s : %s : %s' % (self.equip_type, self.equip_model, self.serial_number)

#def update_equipment(instance, **kwargs):
#    print instance
#    c = instance.equipment
#    c.last_state = equip_last_state(c)
#    c.save()

#models.signals.post_save.connect(update_equipment, sender="IntervEquip") 
#models.signals.post_delete.connect(update_equipment, sender="IntervEquip")

####
#
# Network's section
#
####

# Network
class Network(models.Model):
    FR = 1
    G = 2
    RA = 3
    RD = 4
    AUTRE = 5
    NETWORK = (
        (FR, 'RESIF LB'),
        (G, 'Géoscope'),
        (RA, 'RAP'),
        (RD, 'CEA'),
        (AUTRE, 'Autre'),
    )
    network_code = models.CharField(max_length=5, verbose_name=_("code reseau"))
    network_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom du reseau"))

####
#
# Station's section
#
####

# Type of action that occur on station
class StationAction(models.Model):
    CREER = 1
    INSTALLER = 2
    OPERER = 3
    CONSTATER_DEFAUT = 4
    MAINT_PREV_DISTANTE = 5
    MAINT_CORR_DISTANTE = 6
    MAINT_PREV_SITE = 7
    MAINT_CORR_SITE = 8
    DEMANTELER = 9
    AUTRE = 10
    STATION_ACTIONS = (
        (CREER, 'Créer code station'),
        (INSTALLER, 'Installer station'),
        (OPERER, 'Mettre en opération'),
        (CONSTATER_DEFAUT, 'Constater défaillance'),
        (MAINT_PREV_DISTANTE, 'Effectuer maintenance préventive à distance'),
        (MAINT_CORR_DISTANTE, 'Effectuer maintenance corrective à distance'),
        (MAINT_PREV_SITE, 'Effectuer maintenance préventive sur site'),
        (MAINT_CORR_SITE, 'Effectuer maintenance corrective sur site'),
        (DEMANTELER, 'Démanteler'),
        (AUTRE, 'Autre'),
    )
    station_action_name = models.CharField(max_length=50, null=True, blank=True)
    pass

# Possible state of a station
class StationState(models.Model):
    INSTALLATION = 1
    OPERATION = 2
    DEFAUT = 3
    PANNE = 4
    FERMEE = 5
    AUTRE = 6
    STATION_STATES = (
        (INSTALLATION, 'En installation'),
        (OPERATION, 'En opération'),
        (DEFAUT, 'En défaillance'),
        (PANNE, 'En panne'),
        (FERMEE, 'Fermée'),
        (AUTRE, 'Autre'),
    )
    station_state_name = models.CharField(max_length=50, null=True, blank=True)

class EquipAction(models.Model):
    ACHETER = 1
    TESTER = 2
    INSTALLER = 3
    DESINSTALLER = 4
    CONSTATER_DEFAUT = 5
    MAINT_PREV_DISTANTE = 6
    MAINT_CORR_DISTANTE = 7
    MAINT_PREV_SITE = 8
    MAINT_CORR_SITE = 9
    EXPEDIER = 10
    RECEVOIR = 11
    METTRE_HORS_USAGE = 12
    CONSTATER_DISPARITION = 13
    RETROUVER = 14
    METTRE_AU_REBUT = 15
    AUTRE = 16
    EQUIP_ACTIONS = (
        (ACHETER, 'Acheter'),
        (TESTER, 'Tester'),
        (INSTALLER, 'Installer'),
        (DESINSTALLER, 'Désinstaller'),
        (CONSTATER_DEFAUT, 'Constater défaut'),
        (MAINT_PREV_DISTANTE, 'Effectuer maintenance préventive à distance'),
        (MAINT_CORR_DISTANTE, 'Effectuer maintenance corrective à distance'),
        (MAINT_PREV_SITE, 'Effectuer maintenance préventive sur site'),
        (MAINT_CORR_SITE, 'Effectuer maintenance corrective sur site'),
        (EXPEDIER, 'Expédier'),
        (RECEVOIR, 'Recevoir'),
        (METTRE_HORS_USAGE, 'Mettre hors usage'),
        (CONSTATER_DISPARITION, 'Constater disparition'),
        (RETROUVER, 'Retrouver suite à une disparition'),
        (METTRE_AU_REBUT, 'Mettre au rebut'),
        (AUTRE, 'Autre'),
    )
    equip_action_name = models.CharField(max_length=50, null=True, blank=True)

# Possible state of an equipment
class EquipState(models.Model):
    OPERATION = 1
    A_TESTER = 2
    DISPONIBLE = 3
    DEFAUT = 4
    PANNE = 5
    EN_TRANSIT = 6
    HORS_USAGE = 7
    DISPARU = 8
    AU_REBUT = 9
    AUTRE = 10
    EQUIP_STATES = (
        (OPERATION, 'En opération'),
        (A_TESTER, 'A tester'),
        (DISPONIBLE, 'Disponible'),
        (DEFAUT, 'En défaillance'),
        (PANNE, 'En panne'),
        (EN_TRANSIT, 'En transit'),
        (HORS_USAGE, 'Hors d\'usage'),
        (DISPARU, 'Disparu'),
        (AU_REBUT, 'Au rebut'),
        (AUTRE, 'Autre'),
    )
    equip_state_name = models.CharField(max_length=50, null=True, blank=True)

def get_defaut_operator():
    return Actor.objects.get(actor_name='Inconnu')

# Station or site 
class StationSite(models.Model):
    DT_INSU = 1
    EOST = 2
    IPGP = 3
    ISTERRE = 4
    OCA = 5
    OMP = 6
    OPGC = 7
    OREME = 8
    OSUNA = 9
    AUTRE = 10
    OSU_CHOICES = (
        (DT_INSU, 'DT_INSU'),
        (EOST, 'EOST'),
        (IPGP, 'IPGP'),
        (ISTERRE, 'ISTERRE'),
        (OCA, 'OCA'),
        (OMP, 'OMP'),
        (OPGC, 'OPGC'),
        (OREME, 'OREME'),
        (OSUNA, 'OSUNA'),
        (AUTRE, 'AUTRE'),
    )   

    STATION = 1
    OBSERVATOIRE = 2
    SAV = 3
    NEANT = 4
    AUTRE = 5
    SITE_CHOICES = (
        (STATION, 'Station sismologique'),
        (OBSERVATOIRE, 'Observatoire'),
        (SAV, 'Lieu de service après vente'),
        (NEANT, 'Lieu indéterminé'),
        (AUTRE, 'Autre'),
    )
   
    site_type = models.IntegerField(choices=SITE_CHOICES, default=STATION, verbose_name=_("Type de site"))
    station_code = models.CharField(max_length=40, unique=True, verbose_name=_("code"))
    station_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom site"))
    latitude = models.DecimalField(null=True, blank=True, verbose_name=_("latitude (degre decimal)"), max_digits=8, decimal_places=6)
    longitude = models.DecimalField(null=True, blank=True, verbose_name=_("longitude (degre decimal)"), max_digits=9, decimal_places=6)
    elevation = models.DecimalField(null=True, blank=True, verbose_name=_("elevation (m)"), max_digits=5, decimal_places=1)
    operator = models.ForeignKey("Actor", default=get_defaut_operator, verbose_name=_("operateur"))
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("adresse"))
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("commune"))
    department = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("departement"))
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("region"))
    country =  models.CharField(max_length=50, null=True, blank=True, verbose_name=_("pays"))
    zip_code = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("code postal"))
    contact = models.TextField(null=True, blank=True, verbose_name=_("contact"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        ordering = ['station_code']
        verbose_name = _("site")
        verbose_name_plural = _("A1. Sites")

    def __unicode__(self):
        return self.station_code

# Management of intervention

class Intervention(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    intervention_date = models.DateTimeField(verbose_name=_("date (aaaa-mm-jj)"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        unique_together = ("station", "intervention_date")

    def __unicode__(self):
        return u'%s : %s' % (self.station.station_code, self.intervention_date)

class IntervActor(models.Model):
    intervention = models.ForeignKey("Intervention", verbose_name=_("intervention"))
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Intervenants")

    def __unicode__(self):
        return u'%s : %s' % (self.intervention, self.actor)

class IntervStation(models.Model):
    intervention = models.ForeignKey("Intervention", verbose_name=_("intervention"))
    station_action = models.IntegerField(choices=StationAction.STATION_ACTIONS, verbose_name=_("action"))
    station_state = models.IntegerField(choices=StationState.STATION_STATES, null=True, blank=True, verbose_name=_("etat"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Actions sur le site")

    def __unicode__(self):
        return u'%s' % (self.intervention)

class IntervEquip(models.Model):
    intervention = models.ForeignKey("Intervention", verbose_name=_("intervention"))
    equip_action = models.IntegerField(choices=EquipAction.EQUIP_ACTIONS, verbose_name=_("action"))
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    equip_state = models.IntegerField(choices=EquipState.EQUIP_STATES, verbose_name=_("etat"))
    station = models.ForeignKey("StationSite", null=True, blank=True, verbose_name=_("site"))
    built = models.ForeignKey("Built", null=True, blank=True, verbose_name=_("bati"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Actions sur les equipements")

    def __unicode__(self):
        return u'%s' % (self.intervention)

# Management of station document

def stationdoc_file_name(self, filename):
        return 'stations/%s_%s/%s' % (self.station.id, self.station.station_code, filename)

class StationDoc(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    owner = models.ForeignKey(User)
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_station = models.FileField(storage=fs, verbose_name=_("document"), upload_to=stationdoc_file_name)

    class Meta:
        unique_together = ("station", "document_title", "inscription_date")
        verbose_name = _("Document concernant le site")
        verbose_name_plural = _("G1. Documents concernants le site")

    def __unicode__(self):
        return u'%s %s %s' % (self.station.station_code, self.document_title, self.inscription_date)

# Management of equipment model document

def equipmodeldoc_file_name(self, filename):
    return 'equipments/%s_%s/%s' % (self.equip_model.id, self.equip_model.equip_model_name, filename)

class EquipModelDoc(models.Model):
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
    owner = models.ForeignKey(User)
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip_model = models.FileField(storage=fs, verbose_name=_("document"), upload_to=equipmodeldoc_file_name)

    class Meta:
        unique_together = ("equip_model", "document_title", "inscription_date")
        verbose_name = _("Document du modele d'equipement")
        verbose_name_plural = _("G2. Documents des modeles d'equipement")

    def __unicode__(self):
        return u'%s %s %s' % (self.equip_model.equip_model_name, self.document_title, self.inscription_date)

# Management of equipment document

def equipdoc_file_name(self, filename):
        return 'equipments/%s_%s/%s_%s_%s/%s' % (self.equip.equip_model.id, self.equip.equip_model.equip_model_name, self.equip.id, self.equip.equip_model.equip_model_name, self.equip.serial_number, filename)

class EquipDoc(models.Model):
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
    equip = ChainedForeignKey(
        Equipment,
        chained_field="equip_model",
        chained_model_field="equip_model", 
        show_all=False, 
        auto_choose=True, 
        verbose_name=_("equipement")
    )
    owner = models.ForeignKey(User)
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip = models.FileField(storage=fs, verbose_name=_("document"), upload_to=equipdoc_file_name)

    class Meta:
        unique_together = ("equip", "document_title", "inscription_date")
        verbose_name = _("Document de l'equipement")
        verbose_name_plural = _("G3. Documents des equipements")

    def __unicode__(self):
        return u'%s %s %s %s' % (self.equip.equip_model.equip_model_name, self.equip.serial_number, self.document_title, self.inscription_date)

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
