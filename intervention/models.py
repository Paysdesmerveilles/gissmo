from django.db import models
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel

from place import transitions as ptransition


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    players = models.ManyToManyField('user.Player', through='InterventionPlayer')
    site = models.ForeignKey('place.Site')


class InterventionPlayer(models.Model):
    intervention = models.ForeignKey('Intervention', on_delete=models.CASCADE)
    player = models.ForeignKey('user.Player', on_delete=models.CASCADE)


class ActionSite(models.Model):
    # TODO: Link to a built
    transition = models.IntegerField(
        choices=ptransition.TRANSITION_CHOICES)
    note = models.TextField(null=True, blank=True)
    intervention = models.ForeignKey('Intervention')

    class Meta:
        verbose_name = _('intervention on site')
        verbose_name_plural = _('Site interventions')


class ActionEquipment(models.Model):
    # TODO: link to an equipment
    # TODO: link to equipment transitions
#    transition = models.IntegerField(
#        choices=etransition.TRANSITION_CHOICES)
    # TODO: link to a built
    note = models.TextField(null=True, blank=True)
    intervention = models.ForeignKey('Intervention')

    class Meta:
        verbose_name = _('intervention on equipment')
        verbose_name_plural = _('Equipment interventions')
