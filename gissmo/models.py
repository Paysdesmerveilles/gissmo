# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.timezone import localtime
from django.contrib.auth.models import User

from gissmo.helpers import format_date
from gissmo.tools import make_date_aware

fs = FileSystemStorage(location=settings.UPLOAD_ROOT)


@python_2_unicode_compatible
class Actor(models.Model):
    """
    **Description :** Personne ou entité morale qui est soit opérateur
d'une station ou propriétaire d'un équipement ou impliquée lors
d'une intervention.

    **Attributes :**

    actor_type : integer
        Type d'acteur comme décrit ci-dessous

        **Choices :**

            1 : Observatoire/Laboratoire : OSU

            2 : Instrumentaliste : Personne qui effectue une action sur
            une station

            3 : Organisme : Réseau

            4 : Entreprise : Unite economique de production de biens ou de
            services a but commercial

            5 : Entreprise SAV : Unite economique de production de biens ou de
            services a but commercial qui est opérateur d'un site de type SAV

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
    actor_type = models.IntegerField(
        choices=ACTOR_TYPE_CHOICES,
        default=AUTRE,
        verbose_name=_("Type d\'intervenant"))
    actor_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("nom"))
    actor_note = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("note"))
    actor_parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name=_("Groupe d\'appartenance"))

    class Meta:
        ordering = ['actor_name']
        verbose_name = _("intervenant")
        verbose_name_plural = _("F1. Intervenants")

    def __str__(self):
        return self.actor_name


@python_2_unicode_compatible
class BuiltType(models.Model):
    """
    **Description :** Type de bâti

    **Attributes :**

    built_type_name : char(40)
        Nom que l'on donne au type de bâti
    """

    built_type_name = models.CharField(
        max_length=40,
        verbose_name=_("type de bati"))

    class Meta:
        ordering = ['built_type_name']
        verbose_name = _("type de bati")
        verbose_name_plural = _("T1. Types of building")

    def __str__(self):
        return self.built_type_name


@python_2_unicode_compatible
class Built(models.Model):
    """
    **Description :** Bâti que l'on retrouvre sur le site et qui contient
au moins un équipement

    **Attributes :**

    station : integer (fk)
        Site ou station sur lequel le bâti est présent

    built_type : integer (fk)
        Type de bâti

    built_short_desc : char(40)
        Courte description du bâti afin de nous permettre de distinguer
celui-ci d'un autre bâti

    built_note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    built_type = models.ForeignKey("BuiltType", verbose_name=_("type de bati"))
    built_short_desc = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_("courte description"))
    built_note = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("note"))

    class Meta:
        unique_together = ("station", "built_type", "built_short_desc")
        verbose_name = _("bati")
        verbose_name_plural = _("B1. Batis")

    def __str__(self):
        return u'%s : %s : %s' % (
            self.station.station_code,
            self.built_type.built_type_name,
            self.built_short_desc)


@python_2_unicode_compatible
class EquipSupertype(models.Model):
    """
    **Description :** Catégorie ou supertype auquel est associé l'équipement

    **Attributes :**

    equip_supertype_name : char(40)
        Nom donné à la catégorie ou supertype
    """
    equip_supertype_name = models.CharField(
        max_length=40,
        verbose_name=_("supertype d'equipement"))
    presentation_rank = models.IntegerField()

    class Meta:
        ordering = ['equip_supertype_name']
        verbose_name = _("supertype de l'equipement")
        verbose_name_plural = _("supertypes des equipements")

    def __str__(self):
        return self.equip_supertype_name


@python_2_unicode_compatible
class EquipType(models.Model):
    """
    **Description :** Sous catégorie ou type auquel est associé l'équipement

    **Attributes :**

    equip_supertype : integer (fk)
        Catégorie ou supertype auquel appartient le type d'équipement

    equip_type_name : char(40)
        Nom donné à la sous catégorie ou type
    """
    equip_supertype = models.ForeignKey(
        "EquipSupertype",
        verbose_name=_("supertype d'equipement"))
    equip_type_name = models.CharField(
        max_length=40,
        verbose_name=_("type d'equipement"))
    presentation_rank = models.IntegerField()

    class Meta:
        ordering = ['equip_type_name']
        verbose_name = _("type d'equipement")
        verbose_name_plural = _("types des equipements")

    def __str__(self):
        return self.equip_type_name


@python_2_unicode_compatible
class EquipModel(models.Model):
    """
    **Description :** Modèle de l'équipement attribué par son constructeur ou
nom d'usage utilisé par la communauté des instrumentalistes

    **Attributes :**

    equip_type : integer (fk)
        Sous-catégorie ou type auquel appartient le modèle d'équipement

    equip_model_name : char(50)
        Nom du modèle de l'équipment
    """
    equip_type = models.ForeignKey(
        EquipType,
        verbose_name=_("type d'equipement"))
    equip_model_name = models.CharField(
        max_length=50,
        verbose_name=_("modele d'equipement"))
    manufacturer = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("manufacturier"))

    def _get_supertype(self):
        "Returns the linked EquipSuperType"
        return '%s' % (self.equip_type.equip_supertype)

    _get_supertype.short_description = _('supertype d\'équipement')

    equip_supertype = property(_get_supertype)

    class Meta:
        ordering = ['equip_model_name']
        verbose_name = _("modele d'equipement")
        verbose_name_plural = _("C1. Modeles des equipements")

    def __str__(self):
        return self.equip_model_name


@python_2_unicode_compatible
class ParameterEquip(models.Model):
    equip_model = models.ForeignKey(
        "EquipModel",
        verbose_name=_("modele d'equipement"))
    parameter_name = models.CharField(
        max_length=50,
        verbose_name=_("nom du parametre"))

    class Meta:
        unique_together = ("equip_model", "parameter_name")
        verbose_name = _("parametre equip")
        verbose_name_plural = _("W1. Parametres equip")

    def __str__(self):
        return u'%s : %s' % (self.equip_model, self.parameter_name)


@python_2_unicode_compatible
class ParameterValue(models.Model):
    parameter = models.ForeignKey(
        "ParameterEquip",
        verbose_name=_("Parametre modele d'equipement"))
    value = models.CharField(max_length=50, verbose_name=_("valeur"))
    default_value = models.BooleanField(
        verbose_name=_("valeur par defaut"),
        default=None)

    class Meta:
        unique_together = ("parameter", "value")
        verbose_name = _("valeur du parametre")
        verbose_name_plural = _("X1. Valeurs des parametres")

    # Validation to check that there is only one value choose by default for
    # a parameter
    def clean(self):
        if self.default_value:
            c = ParameterValue.objects.exclude(pk=self.id).filter(
                parameter=self.parameter,
                default_value__exact=True)
            if c:
                raise ValidationError(
                    "The chosen one is already here! Too late")

    def __str__(self):
        return u'%s' % (self.value)


@python_2_unicode_compatible
class Equipment(models.Model):
    """
    **Description :** Tout appareil installé dans une station sismologique ou
conserver dans l'inventaire des OSU

    **Attributes :**

    equip_model : integer (fk)
        Modèle auquel appartient l'équipment

    serial_number : char(50)
        Numéro de série, numéro de produit ou numéro d'inventaire de
l'équipment

    owner : integer (fk)
        Propriétaire de l'équipement

    contact : text
        Champ libre afin d'ajouter des informations sur les contacts

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    equip_model = models.ForeignKey(
        EquipModel,
        verbose_name=_("modele d'equipement")
    )
    serial_number = models.CharField(
        max_length=50,
        verbose_name=_("numero de serie"))
    owner = models.ForeignKey("Actor", verbose_name=_("proprietaire"))
    vendor = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("vendeur"))
    contact = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("contact"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date achat'))

    def _get_type(self):
        "Returns the linked EquipType"
        return '%s' % (self.equip_model.equip_type)

    def _get_supertype(self):
        "Returns the linked EquipSuperType"
        return '%s' % (self.equip_model.equip_type.equip_supertype)

    _get_type.short_description = _('type d\'équipement')
    _get_supertype.short_description = _('supertype d\'équipement')

    equip_type = property(_get_type)
    equip_supertype = property(_get_supertype)

    class Meta:
        unique_together = (
            "equip_model",
            "serial_number")
        verbose_name = _("equipement")
        verbose_name_plural = _("D1. Equipements")

    def __str__(self):
        return u'%s : %s : %s' % (
            self.equip_model.equip_type,
            self.equip_model,
            self.serial_number)

    def check_mandatories_data(self):
        """
        Raise an error if these data are missing:
          * stockage_site
          * purchase_date
        """
        mandatories_fields = [
            ('stockage_site', 'Stockage site'),
            ('purchase_date', 'Purchase date')]
        for field in mandatories_fields:
            if not getattr(self, field[0], None):
                raise ValidationError(
                    _('%(property_name)s property is missing!'),
                    params={'property_name': field[1]}
                )

    def get_or_create_intervention(self):
        """
        Interventions are needed for each equipment.
        If no one, create them.
        """
        intervention, i_created = Intervention.objects.get_or_create(
            station=self.stockage_site,
            intervention_date=make_date_aware(self.purchase_date),
            defaults={'note': 'Automated creation'})
        interv_equip, ie_created = IntervEquip.objects.get_or_create(
            intervention=intervention,
            equip_action=EquipAction.ACHETER,
            equip=self,
            equip_state=EquipState.A_TESTER,
            station=self.stockage_site,
            defaults={'note': 'Automated creation'})
        if ie_created:
            if not self.actor:
                raise ValidationError(
                    _('No logged user'),
                )
            actor = get_object_or_404(Actor, actor_name=self.actor)
            IntervActor.objects.create(
                intervention=intervention,
                actor=actor)

    def __init__(self, *args, **kwargs):
        """
        Permit to add stockage_site and actor as keyword when creating new
        Equipment.
        """
        new_kwargs = {}
        fake_fields = ['stockage_site', 'actor']
        for keyword in kwargs:
            if keyword not in fake_fields:
                new_kwargs[keyword] = kwargs[keyword]
        super(Equipment, self).__init__(*args, **new_kwargs)
        for field in fake_fields:
            setattr(self, field, kwargs.get(field, None))

    def save(self, *args, **kwargs):
        """
        If first time you save the object, then:
          * check stockage_site and purchase_date presence
          * create related interventions
        """
        if not self.id:
            self.check_mandatories_data()
            # First save object
            res = super(Equipment, self).save(*args, **kwargs)
            # Then create intervention if needed
            self.get_or_create_intervention()
            return res
        return super(Equipment, self).save(*args, **kwargs)

####
#
# Network's section
#
####


@python_2_unicode_compatible
class CommentNetworkAuthor(models.Model):
    comment_network = models.ForeignKey(
        "CommentNetwork",
        verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))


@python_2_unicode_compatible
class CommentNetwork(models.Model):
    network = models.ForeignKey("Network", verbose_name=_("reseau"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))


@python_2_unicode_compatible
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

    network_code = models.CharField(
        max_length=5,
        verbose_name=_("network code"))
    network_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("nom du reseau"))
    code = models.CharField(max_length=5, verbose_name=_("code reseau"))
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("date debut (aaaa-mm-jj)"))
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("date fin (aaaa-mm-jj)"))
    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code alternatif"))
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code historique"))
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description"))

    class Meta:
        verbose_name = _("reseau")
        verbose_name_plural = _("N1. Reseaux")

    def __str__(self):
        return self.network_code


@python_2_unicode_compatible
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
    station_action_name = models.CharField(
        max_length=50,
        null=True,
        blank=True)


@python_2_unicode_compatible
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


@python_2_unicode_compatible
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


@python_2_unicode_compatible
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


@python_2_unicode_compatible
class CommentStationSiteAuthor(models.Model):
    comment_station = models.ForeignKey(
        "CommentStationSite",
        verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))


@python_2_unicode_compatible
class CommentStationSite(models.Model):
    station = models.ForeignKey("StationSite", verbose_name=_("site"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))


@python_2_unicode_compatible
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

            4 : NEANT : Unite economique de production de biens ou de services
            à but commercial

            7 : AUTRE : Autre

    station_code : char(40)
        Code attribué au site ou à la station lors de sa création

    site_name : char(50)
        Nom d'usage attribué au site. On y retrouve souvent le nom de la
        commune à proximité.

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

    town : char(100)
        Commune où est située la station

    county : char(100)
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
        Champ dans lequel on peut inscrire un lien vers un outil interne
        (wiki, etc.)
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

    site_type = models.IntegerField(
        choices=SITE_CHOICES,
        default=STATION,
        verbose_name=_("type de site"))
    station_code = models.CharField(
        max_length=40,
        unique=True,
        verbose_name=_("code"))
    site_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("nom site"))
    latitude = models.DecimalField(
        null=True,
        blank=True,
        verbose_name=_("latitude (degre decimal)"),
        max_digits=8,
        decimal_places=6)
    longitude = models.DecimalField(
        null=True,
        blank=True,
        verbose_name=_("longitude (degre decimal)"),
        max_digits=9,
        decimal_places=6)
    elevation = models.DecimalField(
        null=True,
        blank=True,
        verbose_name=_("elevation (m)"),
        max_digits=5,
        decimal_places=1)
    operator = models.ForeignKey("Actor", verbose_name=_("operateur"))
    address = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("adresse"))
    town = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("commune"))
    county = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("departement"))
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_("region"))
    country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("pays"))
    zip_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name=_("code postal"))
    contact = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("contact"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("lien outil interne"))
    station_parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name=_("site referent"))
    geology = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("formation geologique"))
    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code alternatif"))
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code historique"))
    station_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description station"))
    site_description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description site"))
    latitude_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    latitude_pluserror = models.FloatField(null=True, blank=True)
    latitude_minuserror = models.FloatField(null=True, blank=True)
    latitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WSG84")
    longitude_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    longitude_pluserror = models.FloatField(null=True, blank=True)
    longitude_minuserror = models.FloatField(null=True, blank=True)
    longitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WSG84")
    elevation_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="METERS")
    elevation_pluserror = models.FloatField(null=True, blank=True)
    elevation_minuserror = models.FloatField(null=True, blank=True)
    creation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Date création'))

    class Meta:
        ordering = ['station_code']
        verbose_name = _("site")
        verbose_name_plural = _("A1. Sites")

    def __str__(self):
        return self.station_code

    def check_mandatories_data(self):
        """
        Raise an error if these data are missing:
          * project
          * creation_date
        """
        mandatories_fields = [
            ('project', 'Project'),
            ('creation_date', 'Creation date')]
        for field in mandatories_fields:
            if not getattr(self, field[0], None):
                raise ValidationError(
                    _('%(property_name)s property is missing!'),
                    params={'property_name': field[1]}
                )

    def get_or_create_intervention(self):
        """
        Interventions are needed for each new StationSite.
        If no one, create them.
        """
        intervention = Intervention.objects.create(
            station=self,
            intervention_date=make_date_aware(self.creation_date),
            note='Automated creation')
        IntervStation.objects.create(
            intervention=intervention,
            station_action=StationAction.CREER,
            station_state=StationState.INSTALLATION,
            note='Automated creation')
        if not self.actor:
            raise ValidationError(_('No logged user'))
        actor = get_object_or_404(Actor, actor_name=self.actor)
        IntervActor.objects.create(
            intervention=intervention,
            actor=actor)

        # Add station to a project
        project = get_object_or_404(Project, project_name=self.project)
        project.station.add(self.id)

    def __init__(self, *args, **kwargs):
        """
        Permit to add project as keyword when creating new StationSite.
        """
        new_kwargs = {}
        fake_fields = ['project', 'actor']
        for keyword in kwargs:
            if keyword not in fake_fields:
                new_kwargs[keyword] = kwargs[keyword]
        super(StationSite, self).__init__(*args, **new_kwargs)
        for field in fake_fields:
            setattr(self, field, kwargs.get(field, None))

    def save(self, *args, **kwargs):
        """
        Only add new StationSite if it correspond to a specific project.
        If project given, create an new installation intervention on this
        site.
        """
        if not self.id:
            self.check_mandatories_data()
            # First save object
            res = super(StationSite, self).save(*args, **kwargs)
            # Then create intervention if needed
            self.get_or_create_intervention()
            return res
        return super(StationSite, self).save(*args, **kwargs)


@python_2_unicode_compatible
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
    intervention_date = models.DateTimeField(
        verbose_name=_("date (aaaa-mm-jj)"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        unique_together = ("station", "intervention_date")
        verbose_name = _("Intervention")
        verbose_name_plural = _("E1. Interventions")

    def __str__(self):
        return u'%s : %s' % (
            self.station.station_code,
            format_date(self.intervention_date))


@python_2_unicode_compatible
class IntervActor(models.Model):
    """
    **Description :** Acteurs ayant effectués ou présents lors de
l'intervention

    **Attributes :**

    intervention : integer (fk)
        Intervention à laquelle les intervenants ont participé

    actor : integer (fk)
        Intervenant ayant effectué l'intervention ou présent lors de celle-ci

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    intervention = models.ForeignKey(
        "Intervention",
        verbose_name=_("intervention"))
    actor = models.ForeignKey("Actor", verbose_name=_("intervenant"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Intervenants")

    def __str__(self):
        return u'%s : %s' % (self.intervention, self.actor)


@python_2_unicode_compatible
class IntervStation(models.Model):
    """
    **Description :** Détail de l'intervention qui s'est effectuée sur
la station

    **Attributes :**

    intervention : integer (fk)
        Intervention pour laquelle l'action sur la station est répertoriée

    station_action : integer (fk)
        Action principale effectuée lors de l'intervention sur la station

    station_state : integer (fk)
        État dans lequel se retrouve la station à la fin de l'intervention

    note : text
        Champ libre afin d'ajouter des informations supplémentaires
    """
    intervention = models.ForeignKey(
        "Intervention",
        verbose_name=_("intervention"))
    station_action = models.IntegerField(
        choices=StationAction.STATION_ACTIONS,
        verbose_name=_("action"))
    station_state = models.IntegerField(
        choices=StationState.STATION_STATES,
        null=True,
        blank=True,
        verbose_name=_("etat"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Actions sur le site")

    def __str__(self):
        return u'%s' % (self.intervention)


@python_2_unicode_compatible
class IntervEquip(models.Model):
    """
    **Description :** Détail de l'intervention qui s'est effectuée sur
l'équipement

    **Attributes :**

    intervention : integer (fk)
        Intervention pour laquelle les actions sur les équipement sont
répertoriées

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
    intervention = models.ForeignKey(
        "Intervention",
        verbose_name=_("intervention"))
    equip_action = models.IntegerField(
        choices=EquipAction.EQUIP_ACTIONS,
        verbose_name=_("action"))
    equip = models.ForeignKey("Equipment", verbose_name=_("equipement"))
    equip_state = models.IntegerField(
        choices=EquipState.EQUIP_STATES,
        verbose_name=_("etat"))
    station = models.ForeignKey(
        "StationSite",
        null=True,
        blank=True,
        verbose_name=_("site"))
    built = models.ForeignKey(
        "Built",
        null=True,
        blank=True,
        verbose_name=_("bati"))
    note = models.TextField(null=True, blank=True, verbose_name=_("note"))

    class Meta:
        verbose_name_plural = _("Actions sur les equipements")

    def __str__(self):
        return u'%s' % (self.intervention)


@python_2_unicode_compatible
class StationDocType(models.Model):
    stationdoc_type_name = models.CharField(
        max_length=40,
        verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("S1. Types of document (station)")

    def __str__(self):
        return u'%s' % (self.stationdoc_type_name)


def stationdoc_file_name(self, filename):
        return 'stations/%s_%s/%s' % (
            self.station.id,
            self.station.station_code,
            filename)


@python_2_unicode_compatible
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
    document_type = models.ForeignKey(
        StationDocType,
        null=True,
        blank=True,
        verbose_name=_("type de document"))
    document_title = models.CharField(
        max_length=40,
        verbose_name=_("titre document"))
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_station = models.FileField(
        storage=fs,
        verbose_name=_("document"),
        upload_to=stationdoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("lien document prive"))
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))

    class Meta:
        unique_together = ("station", "document_title", "inscription_date")
        verbose_name = _("Document concernant le site")
        verbose_name_plural = _("G1. Documents concernants le site")

    def __str__(self):
        return u'%s %s %s' % (
            self.station.station_code,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class EquipModelDocType(models.Model):
    equipmodeldoc_type_name = models.CharField(
        max_length=40,
        verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("Q1. Types of document (equip. model)")

    def __str__(self):
        return u'%s' % (self.equipmodeldoc_type_name)


def equipmodeldoc_file_name(self, filename):
    return 'equipments/%s_%s/%s' % (
        self.equip_model.id,
        self.equip_model.equip_model_name,
        filename)


@python_2_unicode_compatible
class EquipModelDoc(models.Model):
    """
    **Description :** Documents relatifs à un modèle d'équipement

    **Attributes :**

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
    equip_model = models.ForeignKey(
        EquipModel,
        verbose_name=_("modele d'equipement")
    )
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(
        EquipModelDocType,
        null=True,
        blank=True,
        verbose_name=_("type de document"))
    document_title = models.CharField(
        max_length=40,
        verbose_name=_("titre document"))
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip_model = models.FileField(
        storage=fs,
        verbose_name=_("document"),
        upload_to=equipmodeldoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("lien document prive"))
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))

    class Meta:
        unique_together = ("equip_model", "document_title", "inscription_date")
        verbose_name = _("Document du modele d'equipement")
        verbose_name_plural = _("G2. Documents des modeles d'equipement")

    def __str__(self):
        return u'%s %s %s' % (
            self.equip_model.equip_model_name,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class EquipDocType(models.Model):
    equipdoc_type_name = models.CharField(
        max_length=40,
        verbose_name=_("type de document"))

    class Meta:
        verbose_name_plural = _("R1. Types of document (equipment)")

    def __str__(self):
        return u'%s' % (self.equipdoc_type_name)


def equipdoc_file_name(self, filename):
        return 'equipments/%s_%s/%s_%s_%s/%s' % (
            self.equip.equip_model.id,
            self.equip.equip_model.equip_model_name,
            self.equip.id,
            self.equip.equip_model.equip_model_name,
            self.equip.serial_number,
            filename)


@python_2_unicode_compatible
class EquipDoc(models.Model):
    """
    **Description :** Documents relatifs à un équipement

    **Attributes :**

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
    equip = models.ForeignKey(
        Equipment,
        verbose_name=_("equipement")
    )
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(
        EquipDocType,
        null=True,
        blank=True,
        verbose_name=_("type de document"))
    document_title = models.CharField(
        max_length=40,
        verbose_name=_("titre document"))
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("date inscription (aaaa-mm-jj)"))
    document_equip = models.FileField(
        storage=fs,
        verbose_name=_("document"),
        upload_to=equipdoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("lien document prive"))
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))

    class Meta:
        unique_together = ("equip", "document_title", "inscription_date")
        verbose_name = _("Document de l'equipement")
        verbose_name_plural = _("G3. Documents des equipements")

    def __str__(self):
        return u'%s %s %s %s' % (
            self.equip.equip_model.equip_model_name,
            self.equip.serial_number,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class CommentChannelAuthor(models.Model):
    comment_channel = models.ForeignKey(
        "CommentChannel",
        verbose_name=_("commentaire"))
    author = models.ForeignKey("Actor", verbose_name=_("auteur"))


@python_2_unicode_compatible
class CommentChannel(models.Model):
    channel = models.ForeignKey("Channel", verbose_name=_("canal"))
    value = models.TextField(verbose_name=_("commentaire"))
    begin_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("debut effectivite (aaaa-mm-jj)"))
    end_effective = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("fin effectivite (aaaa-mm-jj)"))


@python_2_unicode_compatible
class CalibrationUnit(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("Nom unite"))
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description"))

    class Meta:
        verbose_name_plural = _("U1. Types of unit")

    def __str__(self):
        return u'%s' % (self.name)


@python_2_unicode_compatible
class DataType(models.Model):
    type_description = models.CharField(
        max_length=50,
        verbose_name=_("type de donnees"))

    class Meta:
        verbose_name_plural = _("V1. Types of collected data")

    def __str__(self):
        return u'%s' % (self.type_description)


@python_2_unicode_compatible
class ChannelCode(models.Model):
    channel_code = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name=_("code du canal"))
    presentation_rank = models.IntegerField(null=True, blank=True)
    validation_rule = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("regle validation"))

    class Meta:
        verbose_name = _("Code du canal")
        verbose_name_plural = _("Z3. Codes des canaux")

    def __str__(self):
        return u'%s' % (self.channel_code)


@python_2_unicode_compatible
class Channel(models.Model):
    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Ouvert'),
        (CLOSE, 'Ferme'),
        (PARTIAL, 'Partiel'),
    )
    """
    CHANNEL_CHOICES = (
        ('BHE','BHE'),('BHN','BHN'),('BHZ','BHZ'),
        ('CHE','CHE'),('CHN','CHN'),('CHZ','CHZ'),
        ('DPE','DPE'),('DPN','DPN'),('DPZ','DPZ'),
        ('EHE','EHE'),('EHN','EHN'),('EHZ','EHZ'),
        ('ELE','ELE'),('ELN','ELN'),('ELZ','ELZ'),
        ('HHE','HHE'),('HHN','HHN'),('HHZ','HHZ'),
        ('LHE','LHE'),('LHN','LHN'),('LHZ','LHZ'),
        ('SHE','SHE'),('SHN','SHN'),('SHZ','SHZ'),
        ('VHE','VHE'),('VHN','VHN'),('VHZ','VHZ'),
        ('LDI','LDI'),('LII','LII'),('LKI','LKI'),
        ('HNE','HNE'),('HNN','HNN'),('HNZ','HNZ'),
        ('BH1','BH1'),('BH2','BH2'),
        ('LH1','LH1'),('LH2','LH2'),
        ('VH1','VH1'),('VH2','VH2'),
        ('HN2','HN2'),('HN3','HN3'),
    )
    """
    station = models.ForeignKey("StationSite", verbose_name=_("station"))
    network = models.ForeignKey('Network', verbose_name=_("code reseau"))
    channel_code = models.ForeignKey(
        'ChannelCode',
        verbose_name=_("code du canal"))
    location_code = models.CharField(
        null=True,
        blank=True,
        max_length=2,
        verbose_name=_("code localisation"))
    latitude = models.DecimalField(
        verbose_name=_("latitude (degre decimal)"),
        max_digits=8,
        decimal_places=6)
    longitude = models.DecimalField(
        verbose_name=_("longitude (degre decimal)"),
        max_digits=9,
        decimal_places=6)
    elevation = models.DecimalField(
        verbose_name=_("elevation (m)"),
        max_digits=5,
        decimal_places=1)
    depth = models.DecimalField(
        verbose_name=_("profondeur (m)"),
        max_digits=4,
        decimal_places=1)
    azimuth = models.DecimalField(
        verbose_name=_("azimut"),
        max_digits=4,
        decimal_places=1)
    dip = models.DecimalField(
        verbose_name=_("angle d'inclinaison"),
        max_digits=3,
        decimal_places=1)
    sample_rate = models.FloatField(verbose_name=_("frequence (Hz)"))

    start_date = models.DateTimeField(
        verbose_name=_("date debut (aaaa-mm-jj)"))
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("date fin (aaaa-mm-jj)"))

    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name=_("etat restrictif"))
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code alternatif"))
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name=_("code historique"))
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_("description"))
    storage_format = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("format de donnees"))
    clock_drift = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("derive horloge (seconds/sample)"))
    calibration_units = models.ForeignKey(
        "CalibrationUnit",
        null=True,
        blank=True,
        verbose_name=_("unite de mesure"))
    data_type = models.ManyToManyField(
        "DataType",
        blank=True,
        verbose_name=_("donnees produites"))
    latitude_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    latitude_pluserror = models.FloatField(null=True, blank=True)
    latitude_minuserror = models.FloatField(null=True, blank=True)
    latitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WSG84")
    longitude_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    longitude_pluserror = models.FloatField(null=True, blank=True)
    longitude_minuserror = models.FloatField(null=True, blank=True)
    longitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WSG84")
    elevation_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="METERS")
    elevation_pluserror = models.FloatField(null=True, blank=True)
    elevation_minuserror = models.FloatField(null=True, blank=True)
    depth_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="METERS")
    depth_pluserror = models.FloatField(null=True, blank=True)
    depth_minuserror = models.FloatField(null=True, blank=True)
    azimuth_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    azimuth_pluserror = models.FloatField(null=True, blank=True)
    azimuth_minuserror = models.FloatField(null=True, blank=True)
    dip_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="DEGREES")
    dip_pluserror = models.FloatField(null=True, blank=True)
    dip_minuserror = models.FloatField(null=True, blank=True)
    sample_rate_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="SAMPLES/S")
    sample_rate_pluserror = models.FloatField(null=True, blank=True)
    sample_rate_minuserror = models.FloatField(null=True, blank=True)
    clock_drift_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="SECONDS/SAMPLE")
    clock_drift_pluserror = models.FloatField(null=True, blank=True)
    clock_drift_minuserror = models.FloatField(null=True, blank=True)
    equipments = models.ManyToManyField(
        Equipment,
        through='Chain',
        verbose_name=_("Equipments"),
    )

    class Meta:
        unique_together = (
            "station",
            "network",
            "channel_code",
            "location_code",
            "start_date")
        verbose_name = _("Canal d'acquisition")
        verbose_name_plural = _("Z1. Canaux d'acquisition")

    def __str__(self):
        return u'%s : %s : %s : %s : %s : %s : %s : %s : %s : %s : %s : %s' % (
            self.station,
            self.network,
            self.location_code,
            self.channel_code,
            self.latitude,
            self.longitude,
            self.elevation,
            self.depth,
            self.dip,
            self.azimuth,
            self.sample_rate,
            localtime(self.start_date).strftime("%Y-%m-%d %H:%M:%S"))


@python_2_unicode_compatible
class Chain(models.Model):
    SENSOR = 1
    PREAMPLIFIER = 2
    DATALOGGER = 3
    EQUIPMENT = 4
    OTHER_1 = 5
    OTHER_2 = 6
    OTHER_3 = 7
    OTHER_4 = 7
    OTHER_5 = 9
    ORDER_CHOICES = (
        (SENSOR, 'Sensor'),
        (PREAMPLIFIER, 'PreAmplifier'),
        (DATALOGGER, 'DataLogger'),
        (EQUIPMENT, 'Equipment'),
        (OTHER_1, 'Other_1'),
        (OTHER_2, 'Other_2'),
        (OTHER_3, 'Other_3'),
        (OTHER_4, 'Other_4'),
        (OTHER_5, 'Other_5'),
    )

    channel = models.ForeignKey('Channel', verbose_name=_("canal"))
    order = models.IntegerField(
        choices=ORDER_CHOICES,
        null=False,
        blank=False,
        verbose_name=_("Type"))
    equip = models.ForeignKey('Equipment', verbose_name=_("equipement"))

    class Meta:
        unique_together = ("channel", "order")
        verbose_name = _("Composante de la chaine d'acqui")
        verbose_name_plural = _("Z2. Composantes des chaines d'acqui")

    def __str__(self):
        return u'%s : %s' % (self.order, self.equip)


@python_2_unicode_compatible
class ChainConfig(models.Model):
    """
    Le nom des paramètres devra respecter la nomenclature XML car ils seront
transformés en TAG dans la section config.

Les noms peuvent contenir des lettres, des chiffres ou d'autres caractères.
Les noms ne peuvent débuter par un nombre ou un signe de ponctuation.
Les noms ne peuvent commencer par les lettres xml (ou XML ou Xml...).
Les noms ne peuvent contenir des espaces.
La longueur des noms est libre mais on conseille de rester raisonnable.
On évitera certains signes qui pourraient selon les logiciels,
prêter à confusion comme "-", ";", ".", "<", ">", etc.

Ne pas utilser les caractères spéciaux (même si en principe cela semble
autorisé).
Les caractères spéciaux pour nous francophones comme é, à, ê, ï, ù sont a
priori permis mais pourraient être mal interprétés par certains programmes.
    """
    # Hack to inline in channel
    channel = models.ForeignKey('Channel', verbose_name=_("canal"))
    chain = models.ForeignKey('Chain', verbose_name=_("chaine d'acquisition"))
    parameter = models.ForeignKey(
        'ParameterEquip',
        verbose_name=_("parametre"))
    value = models.ForeignKey('ParameterValue', verbose_name=_("value"))

    class Meta:
        unique_together = ("channel", "chain", "parameter")

    def __str__(self):
        return u'%s : %s : %s' % (self.chain, self.parameter, self.value)


@python_2_unicode_compatible
class Project(models.Model):
    project_name = models.CharField(max_length=50)
    manager = models.ForeignKey(User)
    station = models.ManyToManyField('StationSite', blank=True)

    # Validation to check that the name of the project ALL don't change
    # It's needed in comparison to the admin.py module to filter station,
    # equipment, intervention
    # in the queryset
    def clean(self):
        if self.id:
            project = get_object_or_404(Project, pk=self.id)
            if project.project_name == 'ALL' and self.project_name != 'ALL':
                raise ValidationError(
                    "We can't change the name for the project ALL")

    def __str__(self):
        return u'%s' % (self.project_name)


@python_2_unicode_compatible
class ProjectUser(models.Model):
    user = models.ForeignKey(User)
    project = models.ManyToManyField('Project')

    class Meta:
        verbose_name = _("Registered project")
        verbose_name_plural = _("Registered projects")

    def __str__(self):
        return u'%s' % (self.user)


class LoggedActions(models.Model):
    event_id = models.BigIntegerField(primary_key=True)
    schema_name = models.TextField()
    table_name = models.TextField()
    # This field type is a guess.
    relid = models.TextField()
    session_user_name = models.TextField(blank=True)
    action_tstamp_tx = models.DateTimeField()
    action_tstamp_stm = models.DateTimeField()
    action_tstamp_clk = models.DateTimeField()
    transaction_id = models.BigIntegerField(null=True, blank=True)
    application_name = models.TextField(blank=True)
    client_addr = models.GenericIPAddressField(null=True, blank=True)
    client_port = models.IntegerField(null=True, blank=True)
    client_query = models.TextField()
    action = models.TextField()
    row_data = models.TextField()
    changed_fields = models.TextField()
    statement_only = models.BooleanField(default=None)

    class Meta:
        managed = False
        db_table = 'logged_actions'
        verbose_name_plural = _("Logged actions")
