from django.db import models


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
    AGENCY = 0
    CUSTOMER_SERVICE = 1
    UNDEFINED = 2
    OTHER = 3
    TEST = 4
    THEORITICAL = 5
    BUILT = 6
    PLACE_TYPE_CHOICES = (
        (AGENCY, 'Agency'),
        (CUSTOMER_SERVICE, 'Customer service place'),
        (UNDEFINED, 'Undefined'),
        (OTHER, 'Other'),
        (TEST, 'Measuring site'),
        (THEORITICAL, 'Theoritical site'),
        (BUILT, 'Built'),
    )

    # fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name="Referent place")
    name = models.CharField(max_length=50, unique=True)
    _type = models.IntegerField(
        choices=PLACE_TYPE_CHOICES,
        default=UNDEFINED,
        verbose_name="Type")
    description = models.TextField(
        null=True,
        blank=True)
    creation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Creation date")
    note = models.TextField(null=True, blank=True)

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
    operator = models.ForeignKey('affiliation.Organism')
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


class PlaceDocument(models.Model):
    place = models.ForeignKey('place.Place')
    document = models.ForeignKey('document.Document')
