from django.db import models


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    place = models.ForeignKey('place.Place')
    operators = models.ManyToManyField('auth.User')
    confirmed = models.BooleanField(default=None)
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s (%s)' % (self.date, self.place)
