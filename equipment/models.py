from django.db import models


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
        verbose_name = "Equipment's type"

    def __str__(self):
        return '%s' % self.name


class Model(models.Model):
    name = models.CharField(max_length=50)
    rank = models.IntegerField()
    manufacturer = models.CharField(
        max_length=50,
        default='Unknown')
    _type = models.ForeignKey('equipment.Type', verbose_name="Type")
    is_network_model = models.BooleanField(
        verbose_name='Network configurable?',
        default=False)
    storage_format = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='Storage format')
    # TODO: get_supertype method for display purposes? Type should be enough

    class Meta:
        verbose_name = "Equipment's model"

    def __str__(self):
        return '%s' % self.name


class Equipment(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Serial number")
    model = models.ForeignKey('equipment.Model')
    owner = models.ForeignKey('user.Player')
    vendor = models.CharField(
        max_length=50,
        null=True,
        blank=True)
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

    # TODO: add link to current state
    # TODO: add link to current place? => Installation of an equipment
    # should be enough. This gives STATE and PLACE.

    def __str__(self):
        return '%s' % self.name


class Parameter(models.Model):
    name = models.CharField(max_length=255, unique=True)
    model = models.ForeignKey('equipment.Model')

    def __str__(self):
        return '%s' % self.name


class Value(models.Model):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return '%s' % self.name


class Configuration(models.Model):
    parameter = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(null=True, blank=True)
    equipment = models.ForeignKey('equipment.Equipment')
