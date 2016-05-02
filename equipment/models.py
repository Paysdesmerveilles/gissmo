from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from equipment import protocols as Protocol
from equipment import states as estate
from equipment import types as etype


class State(models.Model):
    code = models.IntegerField(
        choices=estate.STATE_CHOICES,
        default=estate.UNKNOWN)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(
        blank=True,
        null=True)
    equipment = models.ForeignKey(
        'equipment.Equipment',
        related_name='linked_equipment')

    def allowed_states(self):
        res = []
        if self.code in estate.NEXT_STATES:
            res = estate.NEXT_STATES[self.code]
        return res

    def check_allowed_states(self, state):
        if state not in self.allowed_states():
            raise ValidationError(
                '%s is not allowed for the given state (%s).' % (
                    estate.STATE_CHOICES[state][1],
                    estate.STATE_CHOICES[self.code][1]))

    def process(self, state):
        self.check_allowed_states(state)

        equipment = Equipment.objects.get(pk=self.equipment_id)
        now = timezone.now()

        s = State.objects.create(
            code=state,
            equipment=self.equipment,
            start=now)
        equipment.state = s
        equipment.save()
        self.end = now
        self.save()
        # TODO:
        # - create new one with right link of previous one
        # - add a link to the previous state (to get them linked)

    def __str__(self):
        return '%s' % estate.STATE_CHOICES[self.code][1]


class Type(models.Model):
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Supertype")
    name = models.CharField(max_length=40)
    rank = models.IntegerField()
    # TODO: is_supertype method. If no parent, you're a supertype.

    class Meta:
        verbose_name = "Type"

    def __str__(self):
        return '%s' % self.name


class Model(models.Model):
    # fields
    name = models.CharField(max_length=50)
    rank = models.IntegerField()
    manufacturer = models.CharField(
        max_length=50,
        default='Unknown')
    _type = models.ForeignKey('equipment.Type', verbose_name="Type")
    # Chain_type can be used as a default type for Installation type
    chain_type = models.IntegerField(
        choices=etype.TYPE_CHOICES,
        verbose_name="Acquisition chain type",
        null=True)
    is_network_model = models.BooleanField(
        verbose_name='Network configurable?',
        default=False)
    documents = models.ManyToManyField('document.Document', blank=True)

    class Meta:
        verbose_name = "Model"

    def __str__(self):
        return '%s' % self.name


class Equipment(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Serial number")
    model = models.ForeignKey('equipment.Model')
    owner = models.ForeignKey('affiliation.Organism')
    place = models.ForeignKey('place.Place', related_name='current_place')
    vendor = models.CharField(
        max_length=50,
        null=True,
        blank=True)
    contact = models.ForeignKey('auth.User', blank=True, null=True)
    purchase_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Purchase date')
    clock_drift = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Clock drift")
    clock_drift_unit = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="SECONDS/SAMPLE")
    storage_format = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Storage format')
    documents = models.ManyToManyField('document.Document', blank=True)
    note = models.TextField(null=True, blank=True)
    state = models.ForeignKey(
        'equipment.State',
        related_name='current_state',
        null=True)

    def __str__(self):
        return '%s' % self.name


@receiver(post_save, sender=Equipment)
def create_state(sender, instance, created, **kwargs):
    """
    At first Equipment creation, make a new state with default 'unknown' value
    """
    if created is True:
        s = State.objects.create(equipment=instance)
        instance.state = s
        instance.save()


class ForbiddenEquipmentModel(models.Model):
    # OneToOneField is used not to have multiple line about the same original
    # equipment.
    original = models.OneToOneField(
        'equipment.Model',
        verbose_name='Forbidden Model')
    recommended = models.ForeignKey(
        'equipment.Model',
        verbose_name='Recommended Model',
        related_name='recommended_model')

    class Meta:
        verbose_name = "Forbidden Model"


class Parameter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    model = models.ForeignKey('equipment.Model')

    def __str__(self):
        return '%s' % self.name


class Value(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    parameter = models.ForeignKey('equipment.Parameter')

    def __str__(self):
        return '%s' % self.name


class Configuration(models.Model):
    parameter = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(null=True, blank=True)
    equipment = models.ForeignKey('equipment.Equipment')


class Service(models.Model):
    protocol = models.IntegerField(
        choices=Protocol.PROTOCOL_CHOICES)
    port = models.PositiveIntegerField()
    description = models.CharField(
        max_length=256,
        blank=True,
        null=True)
    equipment = models.ForeignKey('equipment.Equipment')

    def __str__(self):
        return '%s' % Protocol.PROTOCOL_CHOICES[self.protocol][1]


class IPAddress(models.Model):
    ip = models.CharField(
        max_length=255,
        verbose_name='IP Address')  # TODO: add validator for IPAddress
    netmask = models.GenericIPAddressField(
        protocol='both',
        verbose_name='Netmask')
    equipment = models.ForeignKey('Equipment')

    def __str__(self):
        return '%s' % self.ip
