from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

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
        verbose_name = "EC8 Soil classification"

    def __str__(self):
        return '%s' % self.name


class Place(models.Model):
    """
    A place on which you achieve some tasks. As:
      * testing some devices
      * sending broken devices (customer service place)
      * installing a station
      * searching for a new area to install a station
    """
    # Place types
    UNKNOWN = 0
    AGENCY = 1
    THEORITICAL = 2
    MEASURE = 3
    CUSTOMER_SERVICE = 4
    TUNNEL = 5
    DRIFT = 6
    DRAIN = 7
    CAVE = 8
    CELLAR = 9
    UNDERGROUND = 10
    CABINET = 11
    CHAMBER = 12
    PREFABRICATED = 13
    PREMISES = 14
    FORT = 15
    APRON = 16
    SLAB = 17
    OUTSIDE = 18
    WELL = 19
    DRILLING = 20

    PLACE_TYPE_CHOICES = (
        (UNKNOWN, 'Unknown'),
        (AGENCY, 'Agency'),
        (THEORITICAL, 'Theoritical site'),
        (MEASURE, 'Measuring site'),
        (CUSTOMER_SERVICE, 'Customer service place'),
        (TUNNEL, 'Tunnel'),
        (DRIFT, 'Drift'),
        (DRAIN, 'Drain'),
        (CAVE, 'Cave'),
        (CELLAR, 'Cellar'),
        (UNDERGROUND, 'Underground'),
        (CABINET, 'Cabinet'),
        (CHAMBER, 'Chamber'),
        (PREFABRICATED, 'Prefabricated'),
        (PREMISES, 'Premises'),
        (FORT, 'Fort'),
        (APRON, 'Apron'),
        (SLAB, 'Slab'),
        (OUTSIDE, 'Outside'),
        (WELL, 'Well'),
        (DRILLING, 'Drilling'),
    )

    # fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Referent place")
    name = models.CharField(max_length=50)
    _type = models.IntegerField(
        choices=PLACE_TYPE_CHOICES,
        default=UNKNOWN,
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
        verbose_name="EC8 Soil classification")

    # folks
    operators = models.ManyToManyField(
        'affiliation.Organism',
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
    operator = models.ForeignKey('affiliation.Organism')


class PlaceDocument(models.Model):
    place = models.ForeignKey('place.Place')
    document = models.ForeignKey('document.Document')
