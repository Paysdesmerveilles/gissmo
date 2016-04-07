from django.db import models
# from measurement import units


class CommonPosition(models.Model):
    # fields
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
        verbose_name="Referent")
    name = models.CharField(max_length=50, unique=True)
    _type = models.IntegerField(
        choices=SITE_TYPE_CHOICES,
        default=THEORITICAL,  # This is to make user works more about type :)
        verbose_name="Type")
    description = models.TextField(
        null=True,
        blank=True)
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
    operator = models.ForeignKey('affiliation.Organism')
    contact = models.TextField(
        null=True,
        blank=True)

    # files
    documents = models.ManyToManyField(
        'document.Document',
        through='SiteDocument',
        blank=True)

    # TODO: FIXME, Do not permit to register "parent" as itself to avoid
    # problems using parents

    def __str__(self):
        return '%s' % self.name


class SiteDocument(models.Model):
    site = models.ForeignKey('place.Site')
    document = models.ForeignKey('document.Document')


class BuiltType(models.Model):
    name = models.CharField(max_length=40)

    class Meta:
        verbose_name = "Type"

    def __str__(self):
        return '%s' % self.name


class Built(CommonPosition):
    name = models.CharField(
        max_length=40,
        default="Unknown")
    _type = models.ForeignKey("place.BuiltType", verbose_name="Type")
    site = models.ForeignKey("place.Site")
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s' % self.name
