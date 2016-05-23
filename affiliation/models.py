from django.db import models

from affiliation import types as atype


class Agency(models.Model):
    # fields
    name = models.CharField(max_length=255, unique=True)
    _type = models.IntegerField(
        choices=atype.TYPE_CHOICES,
        default=atype.UNKNOWN,
        verbose_name="type")
    users = models.ManyToManyField(
        'auth.User',
        blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Agencies'

    def __str__(self):
        return self.name
