from django.db import models
from django.utils import timezone
from django.db.models.signals import (
    post_save,
    pre_save)
from django.dispatch import receiver
from django.core.exceptions import ValidationError

from polymorphic.models import PolymorphicModel

from measurement import units

from place import states as pstate
from place import transitions as ptransition

class State(PolymorphicModel):
    code = models.IntegerField(
        choices=pstate.STATE_CHOICES)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(
        blank=True,
        null=True)
    site = models.ForeignKey('Site', related_name='linked_site')

    def allowed_transitions(self):
        assert O, "Not implemented"

    def check_transition_allowed(self, transition):
        if transition not in self.allowed_transitions:
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
        site = Site.objects.get(pk=self.site_id)
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
        site = Site.objects.get(pk=self.site_id)
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
        site = Site.objects.get(pk=self.site_id)
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


class CommonPosition(models.Model):
    # fields
    latitude = models.DecimalField(
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitude (°)")
    longitude= models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Longitude (°)",
        max_digits=9,
        decimal_places=6)
    elevation= models.DecimalField(
        null=True,
        blank=True,
        verbose_name="Elevation (m)",
        max_digits=5,
        decimal_places=1)
    latitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WGS84",
        verbose_name="Latitude datum")
    longitude_datum = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        default="WGS84",
        verbose_name="Longitude datum")
    # As we enter all data in degrees or meter (elevation), no need to gives
    # the unit for each one.
#    latitude_unit = models.IntegerField(
#        choices=units.POSITION_UNIT_CHOICES,
#        default=units.DEGREES,
#        null=True,
#        blank=True,
#        verbose_name="Latitude unit")
#    longitude_unit = models.IntegerField(
#        choices=units.POSITION_UNIT_CHOICES,
#        default=units.DEGREES,
#        null=True,
#        blank=True,
#        verbose_name="Longitude unit")
#    elevation_unit = models.IntegerField(
#        choices=units.POSITION_UNIT_CHOICES,
#        default=units.METERS,
#        null=True,
#        blank=True,
#        verbose_name="Elevation unit")

    class Meta:
        abstract = True


class Site(CommonPosition):
    """
    A place on which you achieve some tasks. As:
      * testing some devices
      * sending broken devices (customer service place)
      * installing a station (make a link from a station to a site)
      * have a lot of builts
      * searching for a new area to install a station
    """
    # Site types
    OBSERVATORY = 0
    CUSTOMER_SERVICE = 1
    UNDEFINED = 2
    OTHER = 3
    TEST = 4
    THEORITICAL = 5
    SITE_TYPE_CHOICES = (
        (OBSERVATORY, 'Observatory'),
        (CUSTOMER_SERVICE, 'Customer service place'),
        (UNDEFINED, 'Undefined'),
        (OTHER, 'Other'),
        (TEST, 'Testing site'),
        (THEORITICAL, 'Theoritical site'),
    )

    # fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Referent site")
    name = models.CharField(max_length=50, unique=True)
    _type = models.IntegerField(
        choices=SITE_TYPE_CHOICES,
        default=THEORITICAL,  # This is to make user works more about type :)
        verbose_name="Type")
    description = models.TextField(
        null=True,
        blank=True)
    # TODO: check state design if revelant with GISSMO 2.0 AND MOVE STATE
    # to STATION object in Network as Station is those that change its state
    state = models.ForeignKey('State', null=True, related_name='current_state')
    creation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Creation date")

    # address
    address_street = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Street")
    address_zipcode = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        verbose_name="Zip code")
    address_city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="City")
    address_region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Region")
    address_county = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="District")
    address_country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Country")

    # miscellaneous
    geology = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Geological formation")

    # folks
    operator = models.ForeignKey('user.Player')
    contact = models.TextField(
        null=True,
        blank=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Site)
def create_available_state(sender, instance, created, **kwargs):
    """
    At first creation make a new state 'available' for this Site.
    """
    if created is True:
        a = StateAvailable.objects.create(site=instance)
        instance.state = a
        instance.save()


class BuiltType(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Built type"

    def __str__(self):
        return '%s' % self.name


class Built(CommonPosition):
    name = models.CharField(
        max_length=40,
        default="Unknown")
    _type = models.ForeignKey("place.BuiltType", verbose_name="Type")
    site = models.ForeignKey("place.Site")

    def __str__(self):
        return '%s' % self.name
