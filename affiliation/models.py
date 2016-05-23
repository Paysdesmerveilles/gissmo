from django.db import models


class Agency(models.Model):
    # agency types
    OBSERVATORY = 0
    NETWORK = 1
    BUSINESS = 2
    CUSTOMER_SERVICE = 3
    UNKNOWN = 4
    AGENCY_TYPE_CHOICES = (
        (OBSERVATORY, 'Observatory/Laboratory'),
        (NETWORK, 'Network'),
        (BUSINESS, 'Business'),
        (CUSTOMER_SERVICE, 'Customer service Company'),
        (UNKNOWN, 'Unknown'),
    )

    # fields
    name = models.CharField(max_length=255, unique=True)
    _type = models.IntegerField(
        choices=AGENCY_TYPE_CHOICES,
        default=UNKNOWN,
        verbose_name="type")
    users = models.ManyToManyField(
        'auth.User',
        blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Agencies'

    def __str__(self):
        return self.name
