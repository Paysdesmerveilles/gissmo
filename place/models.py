from django.db import models
from django.utils import timezone
from django.db.models.signals import (
    post_save,
    pre_save)
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from polymorphic import PolymorphicModel

from place import states as pstate

class State(PolymorphicModel):
    code = models.IntegerField(
        choices=pstate.STATE_CHOICES)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(
        blank=True,
        null=True)
    site = models.ForeignKey('Site', related_name='linked_site')

    def doTest(self, isConclusive=False):
        assert 0, "Not implemented"

    def observeFailure(self):
        assert 0, "Not implemented"

    def doFix(self):
        assert 0, "Not implemented"

    def __str__(self):
        return pstate.STATE_CHOICES[self.code][1]


class StateAvailable(State):
    def doTest(self, isConclusive=False):
        print('Test in progress…')
        site = Site.objects.get(pk=self.site_id)
        if isConclusive:
            u = StateUsed.objects.create(site=self.site)
            site.state = u
            site.save()
            print('…used')
        else:

            b = StateBroken.objects.create(site=self.site)
            site.state = b
            site.save()
            print('broken')
        self.end = timezone.now()
        self.save()

    def observeFailure(self):
        assert 0, "You cannot observe Failure on an available Site."

    def doFix(self):
        assert 0, "Site is not broken!"


@receiver(pre_save, sender=StateAvailable)
def get_available_code(sender, instance, **kwargs):
    instance.code = pstate.AVAILABLE


class StateBroken(State):
    def doTest(self, isConclusive=False):
        assert 0, "You cannot make test on a broken Site."

    def observeFailure(self):
        assert 0, "You're already broken"

    def doFix(self):
        print('Fixing…')
        site = Site.objects.get(pk=self.site_id)
        a = StateAvailable.objects.create(site=self.site)
        site.state = a
        site.save()
        print('…available')
        self.end = timezone.now()
        self.save()


@receiver(pre_save, sender=StateBroken)
def get_broken_code(sender, instance, **kwargs):
    instance.code = pstate.BROKEN


class StateUsed(State):
    def doTest(self, isConclusive=False):
        assert 0, "You cannot make test on a used Site."

    def observeFailure(self):
        print('Failure detected!')
        site = Site.objects.get(pk=self.site_id)
        b = StateBroken.objects.create(site=self.site)
        site.state = b
        site.save()
        print('…broken')
        self.end = timezone.now()
        self.save()

    def doFix(self):
        assert 0, "Site is not broken!"


@receiver(pre_save, sender=StateUsed)
def get_used_code(sender, instance, **kwargs):
    instance.code = pstate.USED


class Site(models.Model):
    name = models.CharField(max_length=60, unique=True)
    state = models.ForeignKey('State', null=True, related_name='current_state')

    def __str__(self):
        return self.name


@receiver(post_save, sender=Site)
def create_available_state(sender, instance, created, **kwargs):
    """
    At first creation make a new state 'available' for this Site.
    """
    if created is True:
        a = StateAvailable.objects.create(site=instance)
        instance.state = a
        instance.save()
