from django.db import models

from place.models import CommonPosition

from grid import codes as channel_code

from measurement import units


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
    site = models.ForeignKey('place.Site')

    # folks
    operator = models.ForeignKey('user.Player')

    # files
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s' % self.code


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
    configuration = models.ForeignKey('equipment.Configuration')
    _type = models.IntegerField(
        choices=TYPE_CHOICES,
        verbose_name="Type")
    start = models.DateTimeField(auto_now=True, verbose_name="Starting date")
    end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Ending date')
    depth = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='Depth (m)')

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
        choices = channel_code.CODE_CHOICES)
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
