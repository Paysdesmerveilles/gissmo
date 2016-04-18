from django.db import models


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    place = models.ForeignKey('place.Place')
    protagonists = models.ManyToManyField(
        'auth.User',
        through="intervention.Protagonist")
    organisms = models.ManyToManyField(
        'affiliation.Organism',
        through="intervention.Operator")
    confirmed = models.BooleanField(default=None)
    documents = models.ManyToManyField('document.Document', blank=True)

    def __str__(self):
        return '%s (%s)' % (self.date, self.place)


class Protagonist(models.Model):
    intervention = models.ForeignKey('intervention.Intervention')
    user = models.ForeignKey('auth.User')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Protagonist (interv.)'
        verbose_name_plural = 'Protagonists (interv.)'

    def delete(self, *args, **kwargs):
        """
        Check that, after deletion, we need to also delete related Organism
        """
        intervention_id = self.intervention_id
        res = super(Protagonist, self).delete(*args, **kwargs)
        i = Intervention.objects.get(pk=intervention_id)
        remaining_organisms = []
        for intervuser in i.users.all():
            u = intervuser.user
            for o in u.organism_set.all():
                remaining_organisms.append(o.id)

        current_organisms = []
        for intervorganism in i.organisms.all():
            current_organisms.append(intervorganism.organism_id)

        difference = set(current_organisms) - set(remaining_organisms)

        for organism_id in difference:
            Operator.objects.filter(
                intervention=i,
                organism_id=organism_id).delete()
        return res

    def save(self, *args, **kwargs):
        """
        Add linked organism to the same intervention (if not already
        present)
        """
        res = super(Protagonist, self).save(*args, **kwargs)
        for o in self.user.organism_set.all():
            Operator.objects.get_or_create(
                intervention=self.intervention,
                organism=o)
        return res

    def __str__(self):
        return ''


class Operator(models.Model):
    intervention = models.ForeignKey('intervention.Intervention')
    organism = models.ForeignKey('affiliation.Organism')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Organism (interv.)'
        verbose_name_plural = 'Organisms (interv.)'
