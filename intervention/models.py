from django.db import models


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    site = models.ForeignKey('place.Site')
    operators = models.ManyToManyField('auth.User')
    confirmed = models.BooleanField(default=None)
    documents = models.ManyToManyField('document.Document', blank=True)
