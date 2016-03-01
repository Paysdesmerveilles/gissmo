from django.db import models

class Station(models.Model):
    """
    Station is an object mainly used to generate StationXML file.
    All relative information about place/area are located in Site object.
    """
    # XML status codes
    OPEN = 0
    CLOSE = 1
    PARTIAL = 2
    XML_STATUS_CHOICES = (
        (OPEN, 'Open'),
        (CLOSE, 'Closed'),
        (PARTIAL, 'Partial'),
    )

    # fields
    code = models.CharField(
        max_length=40,
        unique=True)
    description = models.TextField(
        null=True,
        blank=True)
    site = models.ForeignKey('place.Site')

    # folks
    operator = models.ForeignKey('user.Player')

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
