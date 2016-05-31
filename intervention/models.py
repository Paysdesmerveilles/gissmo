from django.db import models


class Intervention(models.Model):
    date = models.DateTimeField(db_index=True)
    note = models.TextField(null=True, blank=True)
    place = models.ForeignKey('place.Place')
    protagonists = models.ManyToManyField(
        'auth.User',
        through="intervention.Protagonist")
    agencies = models.ManyToManyField(
        'affiliation.Agency',
        through="intervention.Operator")
    confirmed = models.BooleanField(default=False)
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
        Check that, after deletion, we need to also delete related Agency
        """
        intervention_id = self.intervention_id
        res = super(Protagonist, self).delete(*args, **kwargs)
        i = Intervention.objects.get(pk=intervention_id)
        remaining_agencies = []
        for intervuser in i.users.all():
            u = intervuser.user
            for o in u.agency_set.all():
                remaining_agencies.append(o.id)

        current_agencies = []
        for intervagency in i.agencies.all():
            current_agencies.append(intervagency.agency_id)

        difference = set(current_agencies) - set(remaining_agencies)

        for agency_id in difference:
            Operator.objects.filter(
                intervention=i,
                agency_id=agency_id).delete()
        return res

    def save(self, *args, **kwargs):
        """
        Add linked agency to the same intervention (if not already
        present)
        """
        res = super(Protagonist, self).save(*args, **kwargs)
        for o in self.user.agency_set.all():
            Operator.objects.get_or_create(
                intervention=self.intervention,
                agency=o)
        return res

    def __str__(self):
        return ''


class Operator(models.Model):
    intervention = models.ForeignKey('intervention.Intervention')
    agency = models.ForeignKey('affiliation.Agency')
    note = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Agency (interv.)'
        verbose_name_plural = 'Agencies (interv.)'
