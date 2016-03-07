from django.db import models


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    site = models.ForeignKey('place.Site')
    players = models.ManyToManyField('user.Player')
    confirmed = models.BooleanField(default=None)
