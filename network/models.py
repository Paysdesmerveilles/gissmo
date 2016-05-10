from django.db import models

from equipment import types as etype
from measurement import units
from network import codes as channel_code


class Station(models.Model):
    """
    Station is an object mainly used to generate StationXML file.
    All relative information about place/area are located in Place object.
    WARNING: 2 stations code could be same. When you install a second station
    on same place that use some same network, then you can use same code.
    """
    # fields
    code = models.CharField(max_length=40)  # 2 codes could be equal
    description = models.TextField(
        null=True,
        blank=True)
    place = models.ForeignKey('place.Place')

    # folks
    operator = models.ForeignKey('affiliation.Organism')

    # files
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s' % self.code


class Network(models.Model):
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


class Installation(models.Model):
    """
    An instance of Equipment as part of Channel creation.
    parent field permit to make a tree of Acquisition Chain
    """
    # fields
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        verbose_name='Connected to')
    equipment = models.ForeignKey('equipment.Equipment')
    place = models.ForeignKey('place.Place')
    configurations = models.ManyToManyField(
        'equipment.Configuration',
        blank=True)
    _type = models.IntegerField(
        choices=etype.TYPE_CHOICES,
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

    # TODO: Create a method that fetch the entire chain (parent and child)

    def __str__(self):
        return '%s (%s) on %s' % (
            etype.TYPE_CHOICES[self._type][1],
            self.equipment,
            self.built)


class Datatype(models.Model):
    """
    As datatypes are specific regarding:
    https://github.com/FDSN/StationXML/blob/master/fdsn-station.xsd#L284
    we need to load them as initial fixtures
    """
    # fields
    name = models.CharField(
        max_length=50)

    def __str__(self):
        return '%s' % self.name


class Channel(models.Model):
    # fields
    installation = models.ForeignKey('network.Installation')
    # TODO: JS Filter on stations regarding Installation (places)
    station = models.ForeignKey('network.Station')
    network = models.ForeignKey('network.Network')
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
    datatypes = models.ManyToManyField(
        'network.Datatype',
        blank=True)
    configurations = models.ManyToManyField(
        'equipment.Configuration',
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
