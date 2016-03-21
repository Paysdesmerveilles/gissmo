from django.db import models


class Organism(models.Model):
    # organism types
    OBSERVATORY = 0
    NETWORK = 1
    BUSINESS = 2
    CUSTOMER_SERVICE = 3
    UNKNOWN = 4
    ORGANISM_TYPE_CHOICES = (
        (OBSERVATORY, 'Observatory/Laboratory'),
        (NETWORK, 'Network'),
        (BUSINESS, 'Business'),
        (CUSTOMER_SERVICE, 'Customer service Company'),
        (UNKNOWN, 'Unknown'),
    )

    # fields
    name = models.CharField(max_length=255)
    _type = models.IntegerField(
        choices=ORGANISM_TYPE_CHOICES,
        default=UNKNOWN,
        verbose_name="type")
    users = models.ManyToManyField(
        'auth.User',
        blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return self.name
