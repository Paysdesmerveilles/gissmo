from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from place import types as ptype
from place import states as pstate


class State(models.Model):
    code = models.IntegerField(
        choices=pstate.STATE_CHOICES,
        default=pstate.AVAILABLE)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(
        blank=True,
        null=True)
    place = models.ForeignKey(
        'place.Place',
        related_name='linked_place')

    def allowed_states(self):
        res = []
        if self.code in pstate.NEXT_STATES:
            res = pstate.NEXT_STATES[self.code]
        return res

    def check_allowed_states(self, state):
        if state not in self.allowed_states():
            raise ValidationError(
                '%s is not allowed for the given state (%s).' % (
                    pstate.STATE_CHOICES[state][1],
                    pstate.STATE_CHOICES[self.code][1]))

    def process(self, state):
        self.check_allowed_states(state)

        place = Place.objects.get(pk=self.place_id)
        now = timezone.now()

        s = State.objects.create(
            code=state,
            place=self.place,
            start=now)
        place.state = s
        place.save()
        self.end = now
        self.save()
        # TODO:
        # - create new one with right link of previous one
        # - add a link to the previous state (to get them linked)

    def __str__(self):
        return '%s' % pstate.STATE_CHOICES[self.code][1]


class GroundType(models.Model):
    name = models.CharField(max_length=2, unique=True)
    description = models.CharField(
        max_length=255)

    class Meta:
        verbose_name = "Soil classification"

    def __str__(self):
        return '%s' % self.name


class Place(models.Model):
    """
    A place on which you achieve some tasks. As:
      * testing some devices
      * sending broken devices (customer service place)
      * installing elements for a station
      * searching for a new area to install a station
    """
    # fields
    name = models.CharField(max_length=50)
    _type = models.IntegerField(
        choices=ptype.TYPE_CHOICES,
        default=ptype.UNKNOWN,
        verbose_name="Type")
    description = models.TextField(
        null=True,
        blank=True)
    creation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Creation date")
    note = models.TextField(null=True, blank=True)
    state = models.ForeignKey(
        'place.State',
        related_name='current_state',
        null=True)

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
    ground_type = models.ForeignKey(
        'GroundType',
        null=True,
        blank=True,
        verbose_name="Soil classification",
        help_text="Following EC8 soil classification. See Pitilakis et al. (Bulletin of Earthquake Engineering, 2012) for details")

    # folks
    operators = models.ManyToManyField(
        'affiliation.Agency',
        through='PlaceOperator',
        blank=True)
    contact = models.TextField(
        null=True,
        blank=True)

    # files
    documents = models.ManyToManyField(
        'document.Document',
        through='PlaceDocument',
        blank=True)

    # GPS fields
    latitude = models.DecimalField(
        null=True,
        blank=True,
        max_digits=9,
        decimal_places=6,
        verbose_name="Latitude (°)")
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

    # TODO: FIXME, Do not permit to register "parent" as itself to avoid
    # problems using parents

    def __str__(self):
        return '%s' % self.name


@receiver(post_save, sender=Place)
def create_state(sender, instance, created, **kwargs):
    """
    At first Place creation, make a new state with default 'available' value
    """
    if created is True:
        s = State.objects.create(place=instance)
        instance.state = s
        instance.save()


class PlaceOperator(models.Model):
    place = models.ForeignKey('place.Place')
    operator = models.ForeignKey('affiliation.Agency')


class PlaceDocument(models.Model):
    place = models.ForeignKey('place.Place')
    document = models.ForeignKey('document.Document')
