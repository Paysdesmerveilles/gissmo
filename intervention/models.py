from django.db import models
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User)

class Intervention(models.Model):
    date = models.DateTimeField(db_index=True,auto_now=True)
    station = models.ForeignKey('place.Site')
    note = models.TextField()
    players = models.ManyToManyField(Player)

    class Meta:
        managed = False
