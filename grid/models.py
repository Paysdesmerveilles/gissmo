from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import (
    post_save,
    pre_save)
from django.dispatch import receiver
from django.utils import timezone

from polymorphic.models import PolymorphicModel

from grid import codes as channel_code
from place.models import CommonPosition
from place import states as pstate
from place import transitions as ptransition
from measurement import units


class State(PolymorphicModel):
    code = models.IntegerField(
        choices=pstate.STATE_CHOICES)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(
        blank=True,
        null=True)
    site = models.ForeignKey('Station', related_name='linked_station')

    def allowed_transitions(self):
        assert 0, "Not implemented"

    def check_transition_allowed(self, transition):
        if transition not in self.allowed_transitions():
            raise ValidationError(
                '%s is not allowed for the given state (%s).' % (
                    ptransition.TRANSITION_CHOICES[transition],
                    self.code))

    def process(self, transition):
        assert 0, "Not implemented"

    def __str__(self):
        return pstate.STATE_CHOICES[self.code][1]


class StateAvailable(State):
    def allowed_transitions(self):
        return [
            ptransition.TEST_FAIL,
            ptransition.TEST_SUCCESS,
        ]

    def doTest(self, isConclusive=False):
        print('Test in progress…')
        site = Station.objects.get(pk=self.site_id)
        if isConclusive:
            u = StateUsed.objects.create(site=self.site)
            site.state = u
            site.save()
            print('…used')
        else:
            b = StateBroken.objects.create(site=self.site)
            site.state = b
            site.save()
            print('broken')
        self.end = timezone.now()
        self.save()

    def process(self, transition):
        self.check_transition_allowed(transition)
        if transition == ptransition.TEST_FAIL:
            return self.doTest(False)
        if transition == ptransition.TEST_SUCCESS:
            return self.doTest(True)


@receiver(pre_save, sender=StateAvailable)
def get_available_code(sender, instance, **kwargs):
    instance.code = pstate.AVAILABLE


class StateBroken(State):
    def allowed_transitions(self):
        return [ptransition.FIX]

    def doFix(self):
        print('Fixing…')
        site = Station.objects.get(pk=self.site_id)
        a = StateAvailable.objects.create(site=self.site)
        site.state = a
        site.save()
        print('…available')
        self.end = timezone.now()
        self.save()

    def process(self, transition):
        self.check_transition_allowed(transition)
        if transition == ptransition.FIX:
            return self.doFix()


@receiver(pre_save, sender=StateBroken)
def get_broken_code(sender, instance, **kwargs):
    instance.code = pstate.BROKEN


class StateUsed(State):
    def allowed_transitions(self):
        return [ptransition.FAILURE]

    def observeFailure(self):
        print('Failure detected!')
        site = Station.objects.get(pk=self.site_id)
        b = StateBroken.objects.create(site=self.site)
        site.state = b
        site.save()
        print('…broken')
        self.end = timezone.now()
        self.save()

    def process(self, transition):
        self.check_transition_allowed(transition)
        if transition == ptransition.FAILURE:
            return self.observeFailure()


@receiver(pre_save, sender=StateUsed)
def get_used_code(sender, instance, **kwargs):
    instance.code = pstate.USED


class CommonXML(models.Model):
    # XML status codes
    OPEN = 0
    CLOSE = 1
    PARTIAL = 2
    XML_STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (PARTIAL, 'Partial'),
    )

    # Used for Station_XML export
    xml_historical_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="StationXML Historical code")
    xml_alternate_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
        verbose_name="StationXML Alternate code")
    xml_restricted_status = models.IntegerField(
        choices=XML_STATUS_CHOICES,
        null=True,
        blank=True,
        verbose_name="StationXML Restricted status")

    class Meta:
        abstract = True


class Station(CommonXML):
    """
    Station is an object mainly used to generate StationXML file.
    All relative information about place/area are located in Site object.
    WARNING: 2 stations code could be same. When you install a second station
    on same place that use some same network, then you can use same code.
    """
    # fields
    code = models.CharField(max_length=40)  # 2 codes could be equal
    description = models.TextField(
        null=True,
        blank=True)
    state = models.ForeignKey('State', null=True, related_name='current_state')
    site = models.ForeignKey('place.Site')

    # folks
    operator = models.ForeignKey('user.Organism')

    # files
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s' % self.code


@receiver(post_save, sender=Station)
def create_available_state(sender, instance, created, **kwargs):
    """
    At first creation make a new state 'available' for this Station.
    """
    if created is True:
        a = StateAvailable.objects.create(site=instance)
        instance.state = a
        instance.save()


class Network(CommonXML):
    code = models.CharField(
        max_length=5)
    name = models.CharField(
        max_length=50,
        null=True,
        blank=True)
    description = models.TextField(
        null=True,
        blank=True)
    start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Starting date")
    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Ending date")

    def __str__(self):
        return '%s' % self.code


class Installation(CommonPosition):
    """
    An instance of Equipment as part of Channel creation.
    parent field permit to make a tree of Acquisition Chain
    """
    # type of installation
    SENSOR = 0
    PREAMPLIFIER = 1
    DATALOGGER = 2
    EQUIPMENT = 3
    OTHER_1 = 4
    OTHER_2 = 5
    OTHER_3 = 6
    OTHER_4 = 7
    OTHER_5 = 8

    TYPE_CHOICES = (
        (SENSOR, 'Sensor'),
        (PREAMPLIFIER, 'Preamplifier'),
        (DATALOGGER, 'Datalogger'),
        (EQUIPMENT, 'Equipment'),
        (OTHER_1, 'Other 1'),
        (OTHER_2, 'Other 2'),
        (OTHER_3, 'Other 3'),
        (OTHER_4, 'Other 4'),
        (OTHER_5, 'Other 5'),
    )

    # fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='Connected to')
    equipment = models.ForeignKey('equipment.Equipment')
    built = models.ForeignKey('place.Built')
    configurations = models.ManyToManyField(
        'equipment.Configuration',
        blank=True)
    _type = models.IntegerField(
        choices=TYPE_CHOICES,
        verbose_name="Type")
    start = models.DateTimeField(
        auto_now=True,
        verbose_name='Starting date')
    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ending date')
    depth = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='Depth (m)')

    # TODO: Create a method that fetch the entire chain (parent and child)

    def __str__(self):
        return '%s (%s) on %s' % (
            self.TYPE_CHOICES[self._type][1],
            self.equipment,
            self.built)


class Channel(CommonXML, CommonPosition):
    # datatypes
    TRIGGERED = 0
    CONTINUOUS = 1
    HEALTH = 2
    GEOPHYSICAL = 3
    WEATHER = 4
    FLAG = 5
    SYNTHESIZED = 6
    INPUT = 7
    EXPERIMENTAL = 8
    MAINTENANCE = 9
    BEAM = 10
    DATATYPE_CHOICES = (
        (TRIGGERED, 'TRIGGERED'),
        (CONTINUOUS, 'CONTINUOUS'),
        (HEALTH, 'HEALTH'),
        (GEOPHYSICAL, 'GEOPHYSICAL'),
        (WEATHER, 'WEATHER'),
        (FLAG, 'FLAG'),
        (SYNTHESIZED, 'SYNTHESIZED'),
        (INPUT, 'INPUT'),
        (EXPERIMENTAL, 'EXPERIMENTAL'),
        (MAINTENANCE, 'MAINTENANCE'),
        (BEAM, 'BEAM'),
    )
    # fields
    installation = models.ForeignKey('grid.Installation')
    network = models.ForeignKey('grid.Network')
    code = models.IntegerField(
        choices=channel_code.CODE_CHOICES)
    location_code = models.CharField(
        null=True,
        blank=True,
        max_length=2,
        verbose_name='Location code')
    azimuth = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='Azimuth (°)')
    dip = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name='DIP (°)')
    sample_rate = models.FloatField(verbose_name='Sample rate (Samples/S)')
    start = models.DateTimeField(verbose_name="Starting date")
    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ending date')
    description = models.TextField(
        null=True,
        blank=True)  # need by stationXML export
    # used units
    calibration_unit = models.IntegerField(
        choices=units.CALIBRATION_CHOICES,
        null=True,
        blank=True,
        verbose_name='Calibration unit')
    datatype = models.IntegerField(
        choices=DATATYPE_CHOICES,
        null=True,
        blank=True)
