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
from django.core.mail import send_mail

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
    **Description :** Personne ou entité morale qui est soit opérateur d'une station ou propriétaire d'un équipement ou impliquée lors d'une intervention
            
    **Attributes :**
  
    actor_type : integer
        Type d'acteur comme décrit ci-dessous

        **Choices :**

            1 : Observatoire/Laboratoire : OSU

            2 : Instrumentaliste : Personne qui effectue une action sur une station

            3 : Organisme : Réseau

            4 : Entreprise : Unite economique de production de biens ou de services a but commercial

            5 : Entreprise SAV : Unite economique de production de biens ou de services a but commercial qui est opérateur d'un site de type SAV

            6 : Inconnu : Inconnu

            7 : Autre : Autre

    actor_name : char(50)
        Nom d'usage donné à l'acteur
  
    actor_note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """

    OBSERVATOIRE = 1
    INSTRUMENTALISTE = 2
    ORGANISME = 3
    ENTREPRISE = 4
    ENTREPRISE_SAV = 5
    INCONNU = 6
    AUTRE = 7
    ACTOR_TYPE_CHOICES = (
        (OBSERVATOIRE, 'Observatoire/Laboratoire'),
        (INSTRUMENTALISTE, 'Ingénieur/Technicien'),
        (ORGANISME, 'Réseau'),
        (ENTREPRISE, 'Entreprise'),
        (ENTREPRISE_SAV, 'Entreprise SAV'),
        (INCONNU, 'Inconnu'),
        (AUTRE, 'Autre'),
    ) 
    actor_type = models.IntegerField(choices=ACTOR_TYPE_CHOICES, default=AUTRE, verbose_name=_("Type d\'intervenant"))
    actor_name = models.CharField(max_length=50, unique=True, verbose_name=_("nom"))
    actor_note = models.TextField(null=True, blank=True, verbose_name=_("note"))
    actor_parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_("Groupe d\'appartenance"))

    class Meta:
        ordering = ['actor_name']
        verbose_name = _("intervenant")
        verbose_name_plural = _("F1. Intervenants")

    def __unicode__(self):
        return self.actor_name

#    def save(self, *args, **kw):
#        if self.pk is not None:
#            send_mail('Changement au niveau des intervenants', 'Il y a eu un changement au niveau des informations sur les intervenants', 'mdutil@unistra.fr',
#            ['mdutil@unistra.fr'], fail_silently=False)
#
#        super(Actor, self).save(*args, **kw)

####
#
# Built's section
#
####
# Type of the built
class BuiltType(models.Model):
    """
    **Description :** Type de bâti
    
    **Attributes :**

    built_type_name : char(40)
        Nom que l'on donne au type de bâti 
    """

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
    **Description :** Bâti que l'on retrouvre sur le site et qui contient au moins un équipement

    **Attributes :**

    station : integer (fk)
        Site ou station sur lequel le bâti est présent

    built_type : integer (fk)
        Type de bâti

    built_short_desc : char(40)
        Courte description du bâti afin de nous permettre de distinguer celui-ci d'un autre bâti

    built_note : text
        Champ libre afin d'ajouter des informations supplémentaires
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
    """
    **Description :** Catégorie ou supertype auquel est associé l'équipement

    **Attributes :**

    equip_supertype_name : char(40)
        Nom donné à la catégorie ou supertype
    """
    equip_supertype_name = models.CharField(max_length=40, verbose_name=_("supertype d'equipement"))

    class Meta:
        ordering = ['equip_supertype_name']
        verbose_name = _("supertype de l'equipement")
        verbose_name_plural = _("supertypes des equipements")

    def __unicode__(self):
        return self.equip_supertype_name

## Type of equipment
class EquipType(models.Model):
    """
    **Description :** Sous catégorie ou type auquel est associé l'équipement

    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient le type d'équipement

    equip_type_name : char(40)
        Nom donné à la sous catégorie ou type
    """
    equip_supertype = models.ForeignKey("EquipSupertype", verbose_name=_("supertype d'equipement"))
    equip_type_name = models.CharField(max_length=40, verbose_name=_("type d'equipement"))

    class Meta:
        ordering = ['equip_type_name',]
        verbose_name = _("type d'equipement")
        verbose_name_plural = _("types des equipements")

    def __unicode__(self):
        return self.equip_type_name

# Models of equipment
class EquipModel(models.Model):
    """
    **Description :** Modèle de l'équipement attribué par son constructeur ou nom d'usage utilisé par la communauté des instrumentalistes

    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient le modèle d'équipement

    equip_type : integer (fk)
        Sous-catégorie ou type auquel appartient le modèle d'équipement

    equip_model_name : char(50)
        Nom du modèle de l'équipment
    """
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
    manufacturer = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("manufacturier"))

    class Meta:
        ordering = ['equip_model_name',]
        verbose_name = _("modele d'equipement")
        verbose_name_plural = _("C1. Modeles des equipements")

    def __unicode__(self):
        return self.equip_model_name

# Parameters 
class ParamEquipModel(models.Model):
    equip_model = models.ForeignKey("EquipModel", verbose_name=_("modele d'equipement"))
    parameter_name = models.CharField(max_length=50, verbose_name=_("nom du parametre"))
    default_value = models.CharField(max_length=50, verbose_name=_("valeur par defaut"))

    class Meta:
        unique_together = ("equip_model", "parameter_name")
        verbose_name = _("parametre")
        verbose_name_plural = _("P1. Parametres")

    def __unicode__(self):
        return u'%s : %s' % (self.equip_model.equip_model_name, self.parameter_name)

#class ParamValue(models.Model):
#    parameter = models.ForeignKey("ParamEquipModel", verbose_name=_("Parametre modele d'equipement"))
#    value = models.CharField(max_length=50, verbose_name=_("valeur"))
#
#    class Meta:
#        unique_together = ("parameter", "value")
#        verbose_name = _("valeur du parametre")
#
#    def __unicode__(self):
#        return u'%s : %s' % (self.parameter, self.value)

def get_defaut_owner():
    return Actor.objects.get(actor_name='DT INSU')

# Equipments
class Equipment(models.Model):
    """
    **Description :** Tout appareil installé dans une station sismologique ou conserver dans l'inventaire des OSU

    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient l'équipement

    equip_type : integer (fk)
        Sous-catégorie ou type auquel appartient l'équipement

    equip_model : integer (fk)
        Modèle auquel appartient l'équipment

    serial_number : char(50)
        Numéro de série, numéro de produit ou numéro d'inventaire de l'équipment

    owner : integer (fk)
        Propriétaire de l'équipement

    contact : text
        Champ libre afin d'ajouter des informations sur les contacts

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
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
    vendor = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("vendeur"))
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

class CommentNetworkAuthor(models.Model):
    comment_network = models.ForeignKey("CommentNetwork", verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))

class CommentNetwork(models.Model):
    network = models.ForeignKey("Network", verbose_name=_("reseau"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("fin effectivite (aaaa-mm-jj)"))

# Network
class Network(models.Model):
    """
    **Description :** Réseau 

    **Attributes :**

    network_code : char(5)
        Code qui est atribué au réseau

    network_name : char(50)
        Nom d'usage que l'on utilise pour dénommer le réseau
    """
    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Ouvert'),
        (CLOSE, 'Ferme'),
        (PARTIAL, 'Partiel'),
    )

    network_code = models.CharField(max_length=5, verbose_name=_("network code"))
    network_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom du reseau"))
    code = models.CharField(max_length=5, verbose_name=_("code reseau"))
    start_date = models.DateTimeField(null=True, blank=True,verbose_name=_("date debut (aaaa-mm-jj)"))
    end_date = models.DateTimeField(null=True, blank=True,verbose_name=_("date fin (aaaa-mm-jj)"))
    restricted_status = models.IntegerField(choices=STATUS,null=True, blank=True, verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code alternatif"))
    historical_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code historique"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))

    class Meta:
        verbose_name = _("reseau")
        verbose_name_plural = _("N1. Reseaux")

    def __unicode__(self):
        return self.network_code

####
#
# Station's section
#
####

# Type of action that occur on station
class StationAction(models.Model):
    """
    **Description :** Action qui peut survenir sur une station

    **Choices :**

        1 : CREER : Créer code station

        2 : INSTALLER : Installer station

        3 : OPERER : Mettre en opération

        4 : CONSTATER DEFAUT : Constater défaillance

        5 : MAINT_PREV_DISTANTE : Effectuer maintenance préventive à distance

        6 : MAINT_CORR_DISTANTE : Effectuer maintenance corrective à distance

        7 : MAINT_PREV_SITE : Effectuer maintenance préventive sur site

        8 : MAINT_CORR_SITE : Effectuer maintenance corrective sur site

        9 : DEMANTELER : Démanteler

        10 : AUTRE : Autre

        11 : DEBUTER_TEST : Débuter test

        12 : TERMINER_TEST : Terminer test

    **Attributes :**

    station_action_name : char(50)
        Nom utilise pour décrire l'action effectuée
    """
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
    DEBUTER_TEST = 11
    TERMINER_TEST = 12
    STATION_ACTIONS = (
        (CREER, 'Créer code station'),
        (INSTALLER, 'Installer station'),
        (DEBUTER_TEST, 'Débuter test'),
        (TERMINER_TEST, 'Terminer test'),
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
    """
    **Description :** Etat dans lequel une station peut se retrouver

    **Choices :**

        1 : INSTALLATION : En installation

        2 : OPERATION : En opération

        3 : DEFAUT : En défaillance

        4 : PANNE : En panne 

        5 : FERMEE : Fermée

        6 : AUTRE : Autre

        7 : EN_TEST : En test

    **Attributes :**

    station_state_name : char(50)
        Nom utilisé pour décrire l'état d'une station
    """
    INSTALLATION = 1
    OPERATION = 2
    DEFAUT = 3
    PANNE = 4
    FERMEE = 5
    AUTRE = 6
    EN_TEST = 7
    STATION_STATES = (
        (INSTALLATION, 'En installation'),
        (EN_TEST, 'En test'),
        (OPERATION, 'En opération'),
        (DEFAUT, 'En défaillance'),
        (PANNE, 'En panne'),
        (FERMEE, 'Fermée'),
        (AUTRE, 'Autre'),
    )
    station_state_name = models.CharField(max_length=50, null=True, blank=True)

class EquipAction(models.Model):
    """
    **Description :** Action qui peut survenir sur un équipement

    **Choices :**

        1 : ACHETER : Acheter

        2 : TESTER : Tester

        3 : INSTALLER : Installer

        4 : DESINSTALLER : Désinstaller

        5 : CONSTATER_DEFAUT : Constater défaut

        6 : MAINT_PREV_DISTANTE : Effectuer maintenance préventive à distance

        7 : MAINT_CORR_DISTANTE : Effectuer maintenance corrective à distance

        8 : MAINT_PREV_SITE : Effectuer maintenance préventive sur site

        9 : MAINT_CORR_SITE : Effectuer maintenance corrective sur site

        10 : EXPEDIER : Expédier

        11 : RECEVOIR : Recevoir

        12 : METTRE_HORS_USAGE : Mettre hors usage

        13 : CONSTATER_DISPARITION : Constater disparition

        14 : RETROUVER : Retrouver suite à une disparition

        15 : METTRE_AU_REBUT : Mettre au rebut

        16 : AUTRE : Autre

    **Attributes :**

    equip_action_name : char(50)
        Nom utilisé pour décrire l'action effectuée
    """
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
    """
    **Description :** Etat dans lequel un équipement peut se retrouver

    **Choices :**

        1 : OPERATION : En opération

        2 : A_TESTER : A tester

        3 : DISPONIBLE : Disponible

        4 : DEFAUT : En défaillance

        5 : PANNE : En panne

        6 : EN_TRANSIT : En transit

        7 : HORS_USAGE : Hors d'usage

        8 : DISPARU : Disparu

        9 : AU_REBUT : Au rebut

        10 : AUTRE : Autre               

    **Attributes :**

    equip_state_name : char(50)
        Nom utilisé pour décrire l'état d'un équipement
    """
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

class CommentStationSiteAuthor(models.Model):
    comment_station = models.ForeignKey("CommentStationSite", verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))

class CommentStationSite(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("fin effectivite (aaaa-mm-jj)"))

def get_defaut_operator():
    return Actor.objects.get(actor_name='Inconnu')

# Station or site 
class StationSite(models.Model):
    """
    **Description :** Site ou station d'intérêt dans le cadre du CLB Resif
             
    **Attributes :**

    site_type : integer (choice)
        Type de site

        **Choices :**

            1 : STATION : 

            2 : OBSERVATOIRE : Personne qui effectue une action sur une station

            3 : SAV : Réseau

            4 : NEANT : Unite economique de production de biens ou de services a but commercial

            7 : AUTRE : Autre

    station_code : char(40)
        Code attribué au site ou à la station lors de sa création 

    site_name : char(50) 
        Nom d'usage attribué au site. On y retrouve souvent le nom de la commune à proximité.

    latitude : decimal(8,6)
        Latitude de la station

    longitude : decimal(9,6)
        Longitude de la station

    elevation : decimal(5,1)
        Elevation de la station par rapport au niveau de la mer

    operator : integer (fk)
        Observatoite/Laboratoire ayant la charge d'opérer la station ou le site

    address : char(100)
        Adresse civique du lieu où est située la station

    city : char(100)
        Commune où est située la station

    department : char(100)
        Département où est située la station

    region : char(100)
        Région où est située la station

    country : char(50)
        Pays où est située la station

    zip_code : char(15)
        Code postal 

    contact : text
        Champ libre afin d'ajouter des informations sur les contacts

    note : text
        Champ libre afin d'ajouter des informations supplémentaires

    private_link : char(200) -- URLFIELD
        Champ dans lequel on peut inscrire un lien vers un outil interne (wiki, etc.)
    """
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
    SITE_TEST = 6
    SITE_THEORIQUE = 7
    SITE_CHOICES = (
        (STATION, 'Station sismologique'),
        (SITE_TEST, 'Site de test'),
        (SITE_THEORIQUE, 'Site théorique'),
        (OBSERVATOIRE, 'Observatoire'),
        (SAV, 'Lieu de service après vente'),
        (NEANT, 'Lieu indéterminé'),
        (AUTRE, 'Autre'),
    )
   
    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Ouvert'),
        (CLOSE, 'Ferme'),
        (PARTIAL, 'Partiel'),
    )

    site_type = models.IntegerField(choices=SITE_CHOICES, default=STATION, verbose_name=_("type de site"))
    station_code = models.CharField(max_length=40, unique=True, verbose_name=_("code"))
    site_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("nom site"))
    latitude = models.DecimalField(null=True, blank=True, verbose_name=_("latitude (degre decimal)"), max_digits=8, decimal_places=6)
    longitude = models.DecimalField(null=True, blank=True, verbose_name=_("longitude (degre decimal)"), max_digits=9, decimal_places=6)
    elevation = models.DecimalField(null=True, blank=True, verbose_name=_("elevation (m)"), max_digits=5, decimal_places=1)
    operator = models.ForeignKey("Actor", default=get_defaut_operator, verbose_name=_("operateur"))
    address = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("adresse"))
    town = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("commune"))
    county = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("departement"))
    region = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("region"))
    country =  models.CharField(max_length=50, null=True, blank=True, verbose_name=_("pays"))
    zip_code = models.CharField(max_length=15, null=True, blank=True, verbose_name=_("code postal"))
    contact = models.TextField(null=True, blank=True, verbose_name=_("contact"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))
    private_link = models.URLField(null=True, blank=True, verbose_name=_("lien outil interne"))
    station_parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_("site referent"))
    geology =  models.CharField(max_length=50, null=True, blank=True, verbose_name=_("formation geologique"))
    restricted_status = models.IntegerField(choices=STATUS,null=True, blank=True, verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code alternatif"))
    historical_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code historique"))
    station_description = models.TextField(null=True, blank=True, verbose_name=_("description station"))
    site_description = models.TextField(null=True, blank=True, verbose_name=_("description site"))
    latitude_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    latitude_pluserror = models.FloatField(null=True, blank=True)
    latitude_minuserror = models.FloatField(null=True, blank=True)
    latitude_datum = models.CharField(max_length=15, null=True, blank=True, default="WSG84")
    longitude_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    longitude_pluserror = models.FloatField(null=True, blank=True)
    longitude_minuserror = models.FloatField(null=True, blank=True)
    longitude_datum = models.CharField(max_length=15, null=True, blank=True, default="WSG84")
    elevation_unit = models.CharField(max_length=15, null=True, blank=True, default="METERS")
    elevation_pluserror = models.FloatField(null=True, blank=True)
    elevation_minuserror = models.FloatField(null=True, blank=True)


    class Meta:
        ordering = ['station_code']
        verbose_name = _("site")
        verbose_name_plural = _("A1. Sites")

    def __unicode__(self):
        return self.station_code

# Management of intervention

class Intervention(models.Model):
    """
    **Description :** Intervention ayant eu lieu dans le cadre de CLB Resif
             
    **Attributes :**

    station : integer (fk)
        Site ou station où a eu lieu l'intervention

    intervention_date : timestamp
        Date et heure à laquelle l'intervention s'est produit

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    intervention_date = models.DateTimeField(verbose_name=_("date (aaaa-mm-jj)"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        unique_together = ("station", "intervention_date")
        verbose_name = _("Intervention")
        verbose_name_plural = _("E1. Interventions")

    def __unicode__(self):
        return u'%s : %s' % (self.station.station_code, self.intervention_date)

class IntervActor(models.Model):
    """
    **Description :** Acteurs ayant effectués ou présents lors de l'intervention
             
    **Attributes :**

    intervention : integer (fk)
        Intervention à laquelle les intervenants ont participé

    actor : integer (fk)
        Intervenant ayant effectué l'intervention ou présent lors de celle-ci

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    intervention = models.ForeignKey("Intervention", verbose_name=_("intervention"))
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Intervenants")

    def __unicode__(self):
        return u'%s : %s' % (self.intervention, self.actor)

class IntervStation(models.Model):
    """
    **Description :** Détail de l'intervention qui s'est effectuée sur la station
             
    **Attributes :**

    intervention : integer (fk)
        Intervention pour laquelle l'action sur la station est répertoriée

    station_action : integer (fk)
        Action principale effectuée lors de l'intervention sur la station

    station_state : integer (fk)
        Etat dans lequel se retrouve la station à la fin de l'intervention

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    intervention = models.ForeignKey("Intervention", verbose_name=_("intervention"))
    station_action = models.IntegerField(choices=StationAction.STATION_ACTIONS, verbose_name=_("action"))
    station_state = models.IntegerField(choices=StationState.STATION_STATES, null=True, blank=True, verbose_name=_("etat"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Actions sur le site")

    def __unicode__(self):
        return u'%s' % (self.intervention)

class IntervEquip(models.Model):
    """
    **Description :** Détail de l'intervention qui s'est effectuée sur l'équipement
             
    **Attributes :**

    intervention : integer (fk)
        Intervention pour laquelle les actions sur les équipement sont répertoriées

    equip_action : integer (choice)
        Action principale effectuée sur un équipement lors de l'intervention

    equip : integer (fk)
        Equipement sur lequel l'action s'est effectuée lors de l'intervention

    equip_state : integer (choice)
        Etat dans lequel se retrouve l'équipement à la fin de l'intervention

    station : integer (fk)
        Station où se retrouve l'équipement à la fin de l'intervention

    built : integer (fk)
        Bâti dans lequel se retrouve l'équipement à la fin de l'intervention

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
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
class StationDocType(models.Model):
    stationdoc_type_name = models.CharField(max_length=40, verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("S1. Types of document (station)")

    def __unicode__(self):
        return u'%s' % (self.stationdoc_type_name)

def stationdoc_file_name(self, filename):
        return 'stations/%s_%s/%s' % (self.station.id, self.station.station_code, filename)

class StationDoc(models.Model):
    """
    **Description :** Documents relatifs à la station
             
    **Attributes :**

    station : integer (fk)
        Station à laquelle se rapporte le document déposé

    owner : integer (fk)
        Utilisateur ayant déposer le document

    document_title : char(40)
        Titre attribué au document

    inscription_date : date
        Date à laquelle le document a été déposé

    document_station : char(100) -- FILEFIELD
        Champ qui contient le chemin d'accès au document
    """

    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(StationDocType, null=True, blank=True, verbose_name=_("type de document"))
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_station = models.FileField(storage=fs, verbose_name=_("document"), upload_to=stationdoc_file_name, blank=True)
    private_link = models.URLField(null=True, blank=True, verbose_name=_("lien document prive"))
    begin_effective = models.DateField(null=True, blank=True, verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(null=True, blank=True, verbose_name=_("fin effectivite (aaaa-mm-jj)"))

    class Meta:
        unique_together = ("station", "document_title", "inscription_date")
        verbose_name = _("Document concernant le site")
        verbose_name_plural = _("G1. Documents concernants le site")

    def __unicode__(self):
        return u'%s %s %s' % (self.station.station_code, self.document_title, self.inscription_date)

# Management of equipment model document
class EquipModelDocType(models.Model):
    equipmodeldoc_type_name = models.CharField(max_length=40, verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("Q1. Types of document (equip. model)")

    def __unicode__(self):
        return u'%s' % (self.equipmodeldoc_type_name)

def equipmodeldoc_file_name(self, filename):
    return 'equipments/%s_%s/%s' % (self.equip_model.id, self.equip_model.equip_model_name, filename)

class EquipModelDoc(models.Model):
    """
    **Description :** Documents relatifs à un modèle d'équipement
             
    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient le modèle d'équipement

    equip_type : integer (fk)
        Sous-catégorie ou type auquel appartient le modèle d'équipement

    equip_model : integer (fk)
        Modèle de l'équipment auquel se rapporte le document

    owner : integer (fk)
        Utilisateur ayant déposer le document déposé

    document_title : char(40)
        Titre attribué au document

    inscription_date : date
        Date à laquelle le document a été déposé

    document_equip_model : char(100) -- FILEFIELD
        Champ qui contient le chemin d'accès au document
    """
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
    document_type = models.ForeignKey(EquipModelDocType, null=True, blank=True, verbose_name=_("type de document"))
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip_model = models.FileField(storage=fs, verbose_name=_("document"), upload_to=equipmodeldoc_file_name, blank=True)
    private_link = models.URLField(null=True, blank=True, verbose_name=_("lien document prive"))
    begin_effective = models.DateField(null=True, blank=True,verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(null=True, blank=True,verbose_name=_("fin effectivite (aaaa-mm-jj)"))

    class Meta:
        unique_together = ("equip_model", "document_title", "inscription_date")
        verbose_name = _("Document du modele d'equipement")
        verbose_name_plural = _("G2. Documents des modeles d'equipement")

    def __unicode__(self):
        return u'%s %s %s' % (self.equip_model.equip_model_name, self.document_title, self.inscription_date)

# Management of equipment document
class EquipDocType(models.Model):
    equipdoc_type_name = models.CharField(max_length=40, verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("R1. Types of document (equipment)")

    def __unicode__(self):
        return u'%s' % (self.equipdoc_type_name)

def equipdoc_file_name(self, filename):
        return 'equipments/%s_%s/%s_%s_%s/%s' % (self.equip.equip_model.id, self.equip.equip_model.equip_model_name, self.equip.id, self.equip.equip_model.equip_model_name, self.equip.serial_number, filename)

class EquipDoc(models.Model):
    """
    **Description :** Documents relatifs à un équipement
             
    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient l'équipement

    equip_type : integer (fk)
        Sous-catégorie ou type auquel appartient l'équipement

    equip_model : integer (fk)
        Modèle auquel appartient l'équipment

    equip : integer (fk)
        Equipement auquel se rapporte le document déposé

    owner : integer (fk)
        Utilisateur ayant déposer le document

    document_title : char(40)
        Titre attribué au document

    inscription_date : date
        Date à laquelle le document a été déposé

    document_equip : char(100) -- FILEFIELD
        Champ qui contient le chemin d'accès au document
    """
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
    document_type = models.ForeignKey(EquipDocType, null=True, blank=True, verbose_name=_("type de document"))
    document_title = models.CharField(max_length=40, verbose_name=_("titre document"))
    inscription_date = models.DateField(verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip = models.FileField(storage=fs, verbose_name=_("document"), upload_to=equipdoc_file_name, blank=True)
    private_link = models.URLField(null=True, blank=True, verbose_name=_("lien document prive"))
    begin_effective = models.DateField(null=True, blank=True,verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(null=True, blank=True,verbose_name=_("fin effectivite (aaaa-mm-jj)"))

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


class CommentChannelAuthor(models.Model):
    comment_channel = models.ForeignKey("CommentChannel", verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))

class CommentChannel(models.Model):
    channel = models.ForeignKey("Channel", verbose_name=_("canal"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(null=True, blank=True,verbose_name=_("fin effectivite (aaaa-mm-jj)"))


class CalibrationUnit(models.Model) :
    name = models.CharField(max_length=50, verbose_name=_("Nom unite"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))

    def __unicode__(self):
        return u'%s' % (self.name)

class DataType(models.Model) :
    type_description = models.CharField(max_length=50, verbose_name=_("Type de donnees"))

    def __unicode__(self):
        return u'%s' % (self.type_description)

class Channel(models.Model) :

    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Ouvert'),
        (CLOSE, 'Ferme'),
        (PARTIAL, 'Partiel'),
    )

    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    network = models.ForeignKey('Network', verbose_name=_("code reseau"))
    channel_code = models.CharField(max_length=3, verbose_name=_("code du canal"), choices=[('BHE','BHE'),('BHN','BHN'),('BHZ','BHZ'),('CHE','CHE'),('CHN','CHN'),('CHZ','CHZ'),('HHE','HHE'),('HHN','HHN'),('HHZ','HHZ'),('LHE','LHE'),('LHN','LHN'),('LHZ','LHZ'),('VHE','VHE'),('VHN','VHN'),('VHZ','VHZ'),('LDI','LDI'),('LII','LII'),('LKI','LKI'),('HNE','HNE'),('HNN','HNN'),('HNZ','HNZ'),('BH1','BH1'),('BH2','BH2'),('LH1','LH1'),('LH2','LH2'),('VH1','VH1'),('VH2','VH2'),('HN2','HN2'),('HN3','HN3'),])
    location_code = models.CharField(null=True, blank=True, max_length=2, verbose_name=_("code localisation"))
    latitude = models.DecimalField(verbose_name=_("latitude (degre decimal)"), max_digits=8, decimal_places=6)
    longitude = models.DecimalField(verbose_name=_("longitude (degre decimal)"), max_digits=9, decimal_places=6)
    elevation = models.DecimalField(verbose_name=_("elevation (m)"), max_digits=5, decimal_places=1)
    depth = models.DecimalField(verbose_name=_("profondeur (m)"), max_digits=4, decimal_places=1)
    azimuth = models.DecimalField(verbose_name=_("azimut"), max_digits=4, decimal_places=1)
    dip = models.DecimalField(verbose_name=_("angle d'inclinaison"), max_digits=3, decimal_places=1)
    sample_rate =  models.FloatField(verbose_name=_("frequence (Hz)"))

    start_date = models.DateTimeField(verbose_name=_("date debut (aaaa-mm-jj)"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("date fin (aaaa-mm-jj)"))

    restricted_status = models.IntegerField(choices=STATUS,null=True, blank=True, verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code alternatif"))
    historical_code = models.CharField(max_length=5,null=True, blank=True, verbose_name=_("code historique"))
    description = models.TextField(null=True, blank=True, verbose_name=_("description"))
    storage_format = models.CharField(max_length=50,null=True, blank=True, verbose_name=_("format de donnees"))
    clock_drift =  models.FloatField(null=True, blank=True, verbose_name=_("derive horloge (seconds/sample)"))
    calibration_units = models.ForeignKey("CalibrationUnit", null=True, blank=True, verbose_name=_("unite de mesure"))
    data_type = models.ManyToManyField("DataType", null=True, blank=True, verbose_name=_("donnees produites"))
    latitude_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    latitude_pluserror = models.FloatField(null=True, blank=True)
    latitude_minuserror = models.FloatField(null=True, blank=True)
    latitude_datum = models.CharField(max_length=15, null=True, blank=True, default="WSG84")
    longitude_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    longitude_pluserror = models.FloatField(null=True, blank=True)
    longitude_minuserror = models.FloatField(null=True, blank=True)
    longitude_datum = models.CharField(max_length=15, null=True, blank=True, default="WSG84")
    elevation_unit = models.CharField(max_length=15, null=True, blank=True, default="METERS")
    elevation_pluserror = models.FloatField(null=True, blank=True)
    elevation_minuserror = models.FloatField(null=True, blank=True)
    depth_unit = models.CharField(max_length=15, null=True, blank=True, default="METERS")
    depth_pluserror = models.FloatField(null=True, blank=True)
    depth_minuserror = models.FloatField(null=True, blank=True)
    azimuth_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    azimuth_pluserror = models.FloatField(null=True, blank=True)
    azimuth_minuserror = models.FloatField(null=True, blank=True)
    dip_unit = models.CharField(max_length=15, null=True, blank=True, default="DEGREES")
    dip_pluserror = models.FloatField(null=True, blank=True)
    dip_minuserror = models.FloatField(null=True, blank=True)
    sample_rate_unit = models.CharField(max_length=15, null=True, blank=True, default="SAMPLES/S")
    sample_rate_pluserror = models.FloatField(null=True, blank=True)
    sample_rate_minuserror = models.FloatField(null=True, blank=True)
    clock_drift_unit = models.CharField(max_length=15, null=True, blank=True, default="SECONDS/SAMPLE")
    clock_drift_pluserror = models.FloatField(null=True, blank=True)
    clock_drift_minuserror = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("station", "network", "channel_code", "location_code", "start_date")
        verbose_name = _("Canal d'acquisition")
        verbose_name_plural = _("Z1. Canaux d'acquisition")

    def __unicode__(self):
        return u'%s : %s : %s : %s : %s : %s : %s : %s : %s : %s : %s : %s : %s' % (self.station, self.network, self.location_code, self.channel_code, self.latitude, self.longitude, self.elevation, self.depth, self.dip, self.azimuth, self.sample_rate, self.start_date, self.end_date)

#class ProtoChannelChain(models.Model) :
#    channel = models.ForeignKey('ProtoChannel', verbose_name=_("canal"))
#    chain = models.ForeignKey('ProtoChain', verbose_name=_("chaine d'acquisition"))

class Chain(models.Model) :
#    name = models.CharField(max_length=50, verbose_name=_("Nom de chaine"))
    channel = models.ForeignKey('Channel', verbose_name=_("canal"))
    order = models.IntegerField(choices=[(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),], null=False, blank=False, verbose_name=_("ordre"))
    equip = models.ForeignKey('Equipment', verbose_name=_("equipement"))

    class Meta:
        unique_together = ("channel", "order")
        verbose_name = _("Composante de la chaine d'acqui")
        verbose_name_plural = _("Z2. Composantes des chaines d'acqui")

    def __unicode__(self):
        return u'%s : %s' % (self.order, self.equip)

class ChainConfig(models.Model) :
    channel = models.ForeignKey('Channel', verbose_name=_("canal")) # Hack to inline in channel
    chain = models.ForeignKey('Chain', verbose_name=_("chaine d'acquisition")) 
    parameter = models.CharField(max_length=50, verbose_name=_("parametre"))
    value = models.CharField(max_length=20, null=True, blank=True, verbose_name=_("valeur"))

    def __unicode__(self):
        return u'%s : %s : %s' % (self.chain, self.parameter, self.value)

#from django.db.models.signals import post_save, post_delete
#from django.dispatch import receiver
#from views import equip_last_state, equip_last_place

#@receiver(post_save, sender=IntervEquip)
#def IntervEquip_post_save_handler(sender, **kwargs):
#    obj = kwargs['instance']
#    print("Post save finished!", obj.equip.id)
#    print(EquipState.EQUIP_STATES[equip_last_state(obj.equip.id)-1][1])
#    print(equip_last_place(obj.equip.id))

#@receiver(post_delete, sender=IntervEquip)
#def IntervEquip_post_delete_handler(sender, **kwargs):
#    obj = kwargs['instance']
#    print("Post delete finished!", obj.equip.id)
#    print(EquipState.EQUIP_STATES[equip_last_state(obj.equip.id)-1][1])
#    print(equip_last_place(obj.equip.id))

