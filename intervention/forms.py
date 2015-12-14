# -*- coding: utf-8 -*-
from django import forms
from django.core.urlresolvers import reverse

from place.models import Site


class InterventionForm(forms.ModelForm):
    """
    Change Site select field to add a javascript Listener on it.
    Only when creating new intervention.
    """
    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)

        if not self.instance.id:
            url = reverse('lookup_transitions')
            self.fields['site'] = forms.ModelChoiceField(
                queryset=Site.objects.all(),
                widget = forms.Select(
                    attrs = {
                        'onchange': "get_transitions(this, '" + url + "');"})
            )
