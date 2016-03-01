# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import python_2_unicode_compatible
from django.shortcuts import get_object_or_404
from django.db import models
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils.timezone import localtime
from django.contrib.auth.models import User

from equipment import states as EquipState
from equipment import actions as EquipAction
from equipment import protocols as Protocol

from station import states as StationState
from station import actions as StationAction

from gissmo.validators import (
    validate_ipaddress,
    validate_equip_model)
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
        (OBSERVATOIRE, 'Observatory/Laboratory'),
        (INSTRUMENTALISTE, 'Engineer/Technician'),
        (ORGANISME, 'Network'),
        (ENTREPRISE, 'Business'),
        (ENTREPRISE_SAV, 'Customer service Company'),
        (INCONNU, 'Unknown'),
        (AUTRE, 'Other'),
    )
    actor_type = models.IntegerField(
        choices=ACTOR_TYPE_CHOICES,
        default=AUTRE,
        verbose_name="Type")
    actor_name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Name")
    actor_note = models.TextField(
        null=True,
        blank=True,
        verbose_name="Note")
    actor_parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Membership group")

    class Meta:
        ordering = ['actor_name']
        verbose_name = "Player"

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
        verbose_name="Built type")

    class Meta:
        ordering = ['built_type_name']
        verbose_name = "Built type"

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
    station = models.ForeignKey("StationSite", verbose_name="Site")
    built_type = models.ForeignKey("BuiltType", verbose_name="Type")
    built_short_desc = models.CharField(
        max_length=40,
        default="Unknown",
        verbose_name="Short description")
    built_note = models.TextField(
        null=True,
        blank=True,
        verbose_name="Note")

    class Meta:
        unique_together = ("station", "built_type", "built_short_desc")
        verbose_name = "Built"

    def __str__(self):
        return '%s' % self.built_short_desc


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
        verbose_name="Name")
    presentation_rank = models.IntegerField()

    class Meta:
        ordering = ['equip_supertype_name']
        verbose_name = "Equipment Supertype"

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
        verbose_name="Supertype")
    equip_type_name = models.CharField(
        max_length=40,
        verbose_name="Type")
    presentation_rank = models.IntegerField()

    class Meta:
        ordering = ['equip_type_name']
        verbose_name = "Equipment type"

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

    manufacturer : char(50)
        Fabricant du modèle d'équipement
    """
    equip_type = models.ForeignKey(
        EquipType,
        verbose_name="Type")
    equip_model_name = models.CharField(
        max_length=50,
        verbose_name="Model")
    manufacturer = models.CharField(
        max_length=50,
        default='Unknown',  # keep it untranslated for functional purposes
        verbose_name="Manufacturer")
    is_network_model = models.BooleanField(
        verbose_name='Network configurable?',
        default=False)

    def _get_supertype(self):
        "Returns the linked EquipSuperType"
        return '%s' % (self.equip_type.equip_supertype)

    _get_supertype.short_description = 'Supertype'

    equip_supertype = property(_get_supertype)

    # Check which Equipment Model don't have any Manufacturer
    def have_a_manufacturer(self):
        if self.manufacturer and self.manufacturer != 'Unknown':
            return True
        return False

    have_a_manufacturer.boolean = True
    have_a_manufacturer.short_description = 'Manufacturer?'

    class Meta:
        ordering = ['equip_model_name']
        verbose_name = "Equipment model"

    def __str__(self):
        return self.equip_model_name


@python_2_unicode_compatible
class ParameterEquip(models.Model):
    equip_model = models.ForeignKey(
        "EquipModel",
        verbose_name="Equipment model")
    parameter_name = models.CharField(
        max_length=50,
        verbose_name="Name")

    class Meta:
        unique_together = ("equip_model", "parameter_name")
        verbose_name = "Equipment's parameter"

    def __str__(self):
        return u'%s : %s' % (self.equip_model, self.parameter_name)


@python_2_unicode_compatible
class ParameterValue(models.Model):
    parameter = models.ForeignKey(
        "ParameterEquip",
        verbose_name="Parameter")
    value = models.CharField(max_length=50, verbose_name="Value")
    default_value = models.BooleanField(
        verbose_name="Default value",
        default=None)

    class Meta:
        unique_together = ("parameter", "value")
        verbose_name = "Parameter's value"

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
        (STATION, 'Seismological station'),
        (SITE_TEST, 'Testing site'),
        (SITE_THEORIQUE, 'Theoretical site'),
        (OBSERVATOIRE, 'Observatory'),
        (SAV, 'Customer service place'),
        (NEANT, 'Undefined'),
        (AUTRE, 'Other'),
    )

    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (PARTIAL, 'Partial'),
    )

    site_type = models.IntegerField(
        choices=SITE_CHOICES,
        default=STATION,
        verbose_name="Type")
    station_code = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Code")
    site_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Name")
    latitude = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Latitude (°)",
        max_digits=8,
        decimal_places=6)
    longitude = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Longitude (°)",
        max_digits=9,
        decimal_places=6)
    elevation = models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Elevation (m)",
        max_digits=5,
        decimal_places=1)
    operator = models.ForeignKey("Actor", verbose_name="Operator")
    address = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Address")
    town = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="City")
    county = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="District")
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Region")
    country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Country")
    zip_code = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Zip code")
    contact = models.TextField(
        null=True,
        blank=True,
        verbose_name="Contact")
    note = models.TextField(null=True, blank=True, verbose_name="Note")
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Specific tool link")
    station_parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Linked site (referent)")
    geology = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Geological formation")
    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name="Restrictive state")
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Alternate code")
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Historical code")
    station_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Station description")
    site_description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Site description")
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
        verbose_name='Creation date')
    last_state = models.IntegerField(
        choices=StationState.STATION_STATES,
        null=True,
        blank=True,
        verbose_name='Last state')

    def get_last_state(self):
        res = None
        intervention = IntervStation.objects.filter(
            intervention__station_id=self.id,
            station_state__isnull=False).order_by(
            '-intervention__intervention_date').first()
        if intervention:
            res = intervention.station_state
        return res

    def get_last_state_display(self):
        return ''

    class Meta:
        ordering = ['station_code']
        verbose_name = "Site"

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
                    '%(property_name)s property is missing!',
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
            raise ValidationError(
                'No actor given. On web admin you need to be logged.')
        actor = get_object_or_404(Actor, actor_name=self.actor)
        IntervActor.objects.create(
            intervention=intervention,
            actor=actor)

        # Add station to a project
        project = get_object_or_404(Project, project_name=self.project)
        project.station.add(self.id)

        # Return expected station state
        return StationState.INSTALLATION

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
            state = self.get_or_create_intervention()
            self.last_state = state
            return res
        return super(StationSite, self).save(*args, **kwargs)


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
        verbose_name="Model",
        validators=[validate_equip_model],
    )
    serial_number = models.CharField(
        max_length=50,
        verbose_name="Serial number")
    owner = models.ForeignKey("Actor", verbose_name="Owner")
    vendor = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Seller")
    contact = models.TextField(
        null=True,
        blank=True,
        verbose_name="Contact")
    note = models.TextField(null=True, blank=True, verbose_name="Note")
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Purchase date')
    # Last state makes equipment display faster. Interventions updates it.
    last_state = models.IntegerField(
        choices=EquipState.EQUIP_STATES,
        null=True,
        blank=True,
        verbose_name='Last state')
    # Last station makes equipment display faster. Interventions updates it.
    last_station = models.ForeignKey(
        StationSite,
        null=True,
        blank=True,
        verbose_name='Last place')

    def _get_type(self):
        "Returns the linked EquipType"
        return '%s' % (self.equip_model.equip_type)

    def _get_supertype(self):
        "Returns the linked EquipSuperType"
        return '%s' % (self.equip_model.equip_type.equip_supertype)

    _get_type.short_description = 'Type'
    _get_supertype.short_description = 'Supertype'

    equip_type = property(_get_type)
    equip_supertype = property(_get_supertype)

    def get_last_state(self):
        res = None
        intervention = self.intervequip_set.filter(
            equip_state__isnull=False).order_by(
            'intervention__intervention_date')[:1].last()
        if intervention:
            res = intervention.equip_state
        return res

    def get_last_state_field(self):
        return "%s" % EquipState.EQUIP_STATES[self.last_state - 1][1]

    def get_last_station(self):
        res = None
        intervention = self.intervequip_set.filter(
            station__isnull=False).order_by(
            '-intervention__intervention_date').first()
        if intervention:
            res = intervention.station
        return res

    class Meta:
        unique_together = (
            "equip_model",
            "serial_number")
        verbose_name = "Equipment"

    def __str__(self):
        return '%s : %s' % (
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
                    '%(property_name)s property is missing!',
                    params={'property_name': field[1]}
                )

    def check_forbidden_equipment_model(self):
        """
        Raise an error if equipment model is forbidden.
        Error message will advice user to use the right one.
        """
        if not self.equip_model:
            return
        forbidden = ForbiddenEquipmentModel.objects.filter(
            original=self.equip_model).first()
        if forbidden:
            raise ValidationError(
                '%(choosen_model)s is forbidden!',
                params={'choosen_model': self.equip_model}
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
                    'No logged user',
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
          * check that no forbidden equipment model is used
        """
        if not self.id:
            self.check_mandatories_data()
            self.check_forbidden_equipment_model()
            # First save object
            res = super(Equipment, self).save(*args, **kwargs)
            # Then create intervention if needed
            self.get_or_create_intervention()
            return res
        return super(Equipment, self).save(*args, **kwargs)


class ForbiddenEquipmentModel(models.Model):
    # OneToOneField is used not to have multiple line about the same original
    # equipment.
    original = models.OneToOneField(
        'EquipModel',
        verbose_name='Forbidden Model')
    recommended = models.ForeignKey(
        'EquipModel',
        verbose_name='Recommended Model',
        related_name='recommended_model')

    class Meta:
        verbose_name = "Forbidden Equipment's model"


class Service(models.Model):
    protocol = models.IntegerField(
        choices=Protocol.PROTOCOL_CHOICES,
        verbose_name='Protocol')
    port = models.PositiveIntegerField(verbose_name='Port')
    description = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name='Description')
    equipment = models.ForeignKey('Equipment')

    def __str__(self):
        return '%s' % Protocol.PROTOCOL_CHOICES[self.protocol][1]


class IPAddress(models.Model):
    ip = models.CharField(
        max_length=255,
        verbose_name='IP Address',
        validators=[validate_ipaddress])
    netmask = models.GenericIPAddressField(
        protocol='both',
        verbose_name='Netmask')
    equipment = models.ForeignKey('Equipment')

    def __str__(self):
        return '%s' % self.ip

####
#
# Network's section
#
####


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
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (PARTIAL, 'Partial'),
    )

    network_code = models.CharField(
        max_length=5,
        verbose_name="Code")
    network_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Name")
    start_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Starting date (yyyy-mm-dd)")
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ending date (yyyy-mm-dd)")
    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name="Restricted status")
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Alternate code")
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Historical code")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description")

    class Meta:
        verbose_name = "Network"

    def __str__(self):
        return self.network_code


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
    station = models.ForeignKey("StationSite", verbose_name="Site")
    intervention_date = models.DateTimeField(
        verbose_name="Date (yyyy-mm-dd)")
    note = models.TextField(null=True, blank=True, verbose_name="Note")

    class Meta:
        unique_together = ("station", "intervention_date")
        verbose_name = "Intervention"

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
        verbose_name="Intervention")
    actor = models.ForeignKey("Actor", verbose_name="Protagonist")
    note = models.TextField(null=True, blank=True, verbose_name="Note")

    class Meta:
        verbose_name = "Protagonist"

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
        verbose_name="Intervention")
    station_action = models.IntegerField(
        choices=StationAction.STATION_ACTIONS,
        verbose_name="Action")
    station_state = models.IntegerField(
        choices=StationState.STATION_STATES,
        null=True,
        blank=True,
        verbose_name="State")
    note = models.TextField(null=True, blank=True, verbose_name="Note")

    class Meta:
        verbose_name = "Site intervention"

    def __str__(self):
        return u'%s' % (self.intervention)

    def save(self, *args, **kwargs):
        """
        Update station state in given Intervention.
        """
        res = super(IntervStation, self).save(*args, **kwargs)
        s = StationSite.objects.get(pk=self.intervention.station_id)
        s.last_state = s.get_last_state()
        s.save()
        return res


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
        verbose_name="Intervention")
    equip_action = models.IntegerField(
        choices=EquipAction.EQUIP_ACTIONS,
        verbose_name="Action")
    equip = models.ForeignKey("Equipment", verbose_name="Equipement")
    equip_state = models.IntegerField(
        choices=EquipState.EQUIP_STATES,
        verbose_name="State")
    station = models.ForeignKey(
        "StationSite",
        null=True,
        blank=True,
        verbose_name="Site")
    built = models.ForeignKey(
        "Built",
        null=True,
        blank=True,
        verbose_name="Built")
    note = models.TextField(null=True, blank=True, verbose_name="Note")

    class Meta:
        verbose_name = "Equipment intervention"

    def __str__(self):
        return u'%s' % (self.intervention)

    def save(self, *args, **kwargs):
        """
        Update equipment in given Intervention:
          - state
          - station
        """
        res = super(IntervEquip, self).save(*args, **kwargs)
        e = Equipment.objects.get(pk=self.equip_id)
        e.last_state = e.get_last_state()
        e.last_station = e.get_last_station()
        e.save()
        return res


@python_2_unicode_compatible
class StationDocType(models.Model):
    stationdoc_type_name = models.CharField(
        max_length=40,
        verbose_name="Type")

    class Meta:
        verbose_name = "Document type (station)"
        verbose_name_plural = "Document types (station)"

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

    station = models.ForeignKey("StationSite", verbose_name="Site")
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(
        StationDocType,
        null=True,
        blank=True,
        verbose_name="Type")
    document_title = models.CharField(
        max_length=40,
        verbose_name="Title")
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Registration date (yyyy-mm-dd)")
    document_station = models.FileField(
        storage=fs,
        verbose_name="Document",
        upload_to=stationdoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Private document link")
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective starting date (yyyy-mm-dd)")
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective ending date (yyyy-mm-dd)")

    class Meta:
        unique_together = ("station", "document_title", "inscription_date")
        verbose_name = "Document (station)"
        verbose_name_plural = "Documents (station)"

    def __str__(self):
        return u'%s %s %s' % (
            self.station.station_code,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class EquipModelDocType(models.Model):
    equipmodeldoc_type_name = models.CharField(
        max_length=40,
        verbose_name="Type")

    class Meta:
        verbose_name = "Document type (equip. model)"
        verbose_name_plural = "Document types (equip. model)"

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
        verbose_name="Equipment model"
    )
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(
        EquipModelDocType,
        null=True,
        blank=True,
        verbose_name="Type")
    document_title = models.CharField(
        max_length=40,
        verbose_name="Title")
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Registration date (yyyy-mm-dd)")
    document_equip_model = models.FileField(
        storage=fs,
        verbose_name="Document",
        upload_to=equipmodeldoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Private document link")
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective starting date (yyyy-mm-dd)")
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective ending date (yyyy-mm-dd)")

    class Meta:
        unique_together = ("equip_model", "document_title", "inscription_date")
        verbose_name = "Document (equip.'s model)"
        verbose_name_plural = "Documents (equip.'s model)"

    def __str__(self):
        return u'%s %s %s' % (
            self.equip_model.equip_model_name,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class EquipDocType(models.Model):
    equipdoc_type_name = models.CharField(
        max_length=40,
        verbose_name="Type")

    class Meta:
        verbose_name = "Document type (equip.)"
        verbose_name_plural = "Document types (equip.)"

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
        verbose_name="Equipement"
    )
    owner = models.ForeignKey(User)
    document_type = models.ForeignKey(
        EquipDocType,
        null=True,
        blank=True,
        verbose_name="Type")
    document_title = models.CharField(
        max_length=40,
        verbose_name="Title")
    inscription_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Registration date (yyyy-mm-dd)")
    document_equip = models.FileField(
        storage=fs,
        verbose_name="Document",
        upload_to=equipdoc_file_name,
        blank=True)
    private_link = models.URLField(
        null=True,
        blank=True,
        verbose_name="Private document link")
    begin_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective starting date (yyyy-mm-dd)")
    end_effective = models.DateField(
        null=True,
        blank=True,
        verbose_name="Effective ending date (yyyy-mm-dd)")

    class Meta:
        unique_together = ("equip", "document_title", "inscription_date")
        verbose_name = "Document (equip.)"
        verbose_name_plural = "Documents (equip.)"

    def __str__(self):
        return u'%s %s %s %s' % (
            self.equip.equip_model.equip_model_name,
            self.equip.serial_number,
            self.document_title,
            self.inscription_date)


@python_2_unicode_compatible
class CalibrationUnit(models.Model):
    name = models.CharField(max_length=50, verbose_name="Name")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description")

    class Meta:
        verbose_name = "Unit type"

    def __str__(self):
        return u'%s' % (self.name)


@python_2_unicode_compatible
class DataType(models.Model):
    type_description = models.CharField(
        max_length=50,
        verbose_name="Type")

    class Meta:
        verbose_name = "Data type"

    def __str__(self):
        return u'%s' % (self.type_description)


@python_2_unicode_compatible
class ChannelCode(models.Model):
    channel_code = models.CharField(
        max_length=3,
        primary_key=True,
        verbose_name="Code")
    presentation_rank = models.IntegerField(null=True, blank=True)
    validation_rule = models.TextField(
        null=True,
        blank=True,
        verbose_name="Validation rule")

    class Meta:
        verbose_name = "Channel code"

    def __str__(self):
        return u'%s' % (self.channel_code)


@python_2_unicode_compatible
class Channel(models.Model):
    OPEN = 1
    CLOSE = 2
    PARTIAL = 3
    STATUS = (
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (PARTIAL, 'Partial'),
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
    station = models.ForeignKey("StationSite", verbose_name="Station")
    network = models.ForeignKey('Network', verbose_name="Network")
    channel_code = models.ForeignKey(
        'ChannelCode',
        verbose_name="Channel code")
    location_code = models.CharField(
        null=True,
        blank=True,
        max_length=2,
        verbose_name="Location code")
    latitude = models.DecimalField(
        verbose_name="Latitude (°)",
        max_digits=8,
        decimal_places=6)
    longitude = models.DecimalField(
        verbose_name="Longitude (°)",
        max_digits=9,
        decimal_places=6)
    elevation = models.DecimalField(
        verbose_name="Elevation (m)",
        max_digits=5,
        decimal_places=1)
    depth = models.DecimalField(
        verbose_name="Depth (m)",
        max_digits=4,
        decimal_places=1)
    azimuth = models.DecimalField(
        verbose_name="Azimut",
        max_digits=4,
        decimal_places=1)
    dip = models.DecimalField(
        verbose_name="Dip",
        max_digits=3,
        decimal_places=1)
    sample_rate = models.FloatField(verbose_name="Sample rate (Hz)")

    start_date = models.DateTimeField(
        verbose_name="Starting date (yyyy-mm-dd)")
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ending date (yyyy-mm-dd)")

    restricted_status = models.IntegerField(
        choices=STATUS,
        null=True,
        blank=True,
        verbose_name="Restrictive state")
    alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Alternate code")
    historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="Historical code")
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="Description")
    storage_format = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Storage format")
    clock_drift = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Clock drift (seconds/sample)")
    calibration_units = models.ForeignKey(
        "CalibrationUnit",
        null=True,
        blank=True,
        verbose_name="Calibration unit")
    data_type = models.ManyToManyField(
        "DataType",
        blank=True,
        verbose_name="Produced data")
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
        verbose_name="Equipments",
    )

    class Meta:
        unique_together = (
            "station",
            "network",
            "channel_code",
            "location_code",
            "start_date")
        verbose_name = "Channel"

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
    # WARNING: DO NOT CHANGE these values as they are used in stationXML
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

    channel = models.ForeignKey('Channel', verbose_name="Channel")
    order = models.IntegerField(
        choices=ORDER_CHOICES,
        null=False,
        blank=False,
        verbose_name="Type")
    equip = models.ForeignKey('Equipment', verbose_name="Equipement")

    class Meta:
        unique_together = ("channel", "order")
        verbose_name = "Acquisition chain"

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
    channel = models.ForeignKey('Channel', verbose_name="Channel")
    chain = models.ForeignKey('Chain', verbose_name="Acquisition chain")
    parameter = models.ForeignKey(
        'ParameterEquip',
        verbose_name="Parameter")
    value = models.ForeignKey('ParameterValue', verbose_name="Value")

    class Meta:
        unique_together = ("channel", "chain", "parameter")
        verbose_name = "Configuration"

    def __str__(self):
        return u'%s : %s : %s' % (self.chain, self.parameter, self.value)


@python_2_unicode_compatible
class Project(models.Model):
    project_name = models.CharField(max_length=50, verbose_name="Name")
    manager = models.ForeignKey(User)
    station = models.ManyToManyField(
        'StationSite',
        blank=True,
        verbose_name="Site")

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

    class Meta:
        verbose_name = "Project"

    def __str__(self):
        return u'%s' % (self.project_name)


@python_2_unicode_compatible
class ProjectUser(models.Model):
    user = models.ForeignKey(User)
    project = models.ManyToManyField('Project')

    class Meta:
        verbose_name = "Project's user"

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
        verbose_name = "Logged action"
