# coding=utf-8

from django import forms
from django.contrib.admin import widgets
from django.db.models import Q
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from models import Actor, EquipModelDoc, Equipment, EquipDoc, StationSite, StationDoc 

# TODO Voir a deplacer dans un autre fichier
from views import equip_last_state, equip_last_place, equip_state_todate, equip_place_todate

# TODO Eliminer EquipAction, EquipState, StationAction, StationState
from models import EquipAction, EquipState, StationAction, StationState

"""
Devra aller dans widget.py
"""
class AdminFileWidget(forms.FileInput):
    """
    A FileField Widget that shows its current value if it has one.
    """
    def __init__(self, attrs={}):
        self.app_label = attrs['app_label']
        self.model_name = attrs['model_name']
        self.field_name = attrs['field_name']
        self.id = attrs['id']
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        url = ''
        if value:
            liste = value.url.split('/')
        url = reverse('get_file', args=[self.app_label, self.model_name, self.field_name, self.id])

        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), url, value.name.split('/')[-1], _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class EquipModelDocInlineForm(forms.ModelForm):
    """ 
    Champ pour faire en sorte que les forms inline instancier 
    soit toujours avec un flag has_changed a True
    De cette facon si on change le supertype, type ou le modele du parent cela se repercute aux enfants    
    """
    always_update = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = EquipModelDoc

    def __init__(self, *args, **kwargs):
        super(EquipModelDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            self.fields['always_update'].initial = int(time.time())

class EquipDocInlineForm(forms.ModelForm):
    """ 
    Champ pour faire en sorte que les forms inline instancier 
    soit toujours avec un flag has_changed a True
    De cette facon si on change le supertype, type ou le modele du parent cela se repercute aux enfants    
    """
    always_update = forms.IntegerField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = EquipDoc

    def __init__(self, *args, **kwargs):
        super(EquipDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['always_update'].initial = int(time.time())
            self.fields['document_equip'].widget = AdminFileWidget(attrs={'app_label':instance_document._meta.app_label, 'model_name':instance_document._meta.object_name.lower(), 'field_name':'document_equip', 'id':instance_document.id})

class EquipmentForm(forms.ModelForm):
    """
    Add of fields to obtain the date of purchase and stockage_site only when it'a new station 
    else hide the field and the label
    Only the site of type OBSERVATOIRE can be a stockage site
    """
    observatories = StationSite.objects.filter(site_type=StationSite.OBSERVATOIRE)
    OBS_CHOICES = []
    for obs in observatories:
        OBS_CHOICES.append((obs.id, obs.__unicode__()))
    purchase_date = forms.DateField(widget=widgets.AdminDateWidget,label='Date achat',required=False)
    stockage_site = forms.IntegerField(widget=forms.Select(choices=OBS_CHOICES),required=False)

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['purchase_date'].widget = forms.HiddenInput()
            self.fields['purchase_date'].label = ""
            self.fields['stockage_site'].widget = forms.HiddenInput()
            self.fields['stockage_site'].label = ""
        else:
            self.fields['purchase_date'].required = True
            self.fields['stockage_site'].required = True

    class Meta:
        model = Equipment

class StationDocInlineForm(forms.ModelForm):
    """
    """
    class Meta:
        model = StationDoc

    def __init__(self, *args, **kwargs):
        super(StationDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['document_station'].widget = AdminFileWidget(attrs={'app_label':instance_document._meta.app_label, 'model_name':instance_document._meta.object_name.lower(), 'field_name':'document_station', 'id':instance_document.id})

class StationSiteForm(forms.ModelForm):
    """
    Add of a field to obtain the date of the creation only when it'a new station 
    else hide the field and the label
    """
    creation_date = forms.DateField(widget=widgets.AdminDateWidget,label='Date creation',required=False)

    def __init__(self, *args, **kwargs):
        super(StationSiteForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['creation_date'].widget = forms.HiddenInput()
            self.fields['creation_date'].label = ""
        else:
            self.fields['creation_date'].required = True

        self.fields['operator'].queryset = Actor.objects.filter(Q(actor_type=Actor.OBSERVATOIRE) | Q(actor_type=Actor.ENTREPRISE_SAV) | Q(actor_type=Actor.INCONNU))

    class Meta:
        model = StationSite

class IntervActorInlineFormset(forms.models.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        """
        Grabs the curried initial values and stores them into a 'private'
        variable. Note: the use of self.__initial is important, using
        self.initial or self._initial will be erased by a parent class
        """
        self.__initial = kwargs.pop('initial', [])
        super(IntervActorInlineFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(IntervActorInlineFormset, self).add_fields(form, index)

        if self.__initial:
            actor = get_object_or_404(Actor, actor_name=self.__initial[0])
            form.fields['actor'].initial = actor
    
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        # get forms that actually have valid data
        delete_checked = 0
        form_number = 0
        for form in self.forms:
            # Acquire data for each field
            if form.cleaned_data != {}:
                if form.cleaned_data['DELETE']:
                    delete_checked += 1
                # TODO vue de validation
                # Validation of station_action and final state
                form_number += 1
 
        if form_number == 0 or form_number == delete_checked:  
            raise forms.ValidationError('Au moins un intervenant par intervention')

class IntervEquipInlineFormset(forms.models.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(IntervEquipInlineFormset, self).add_fields(form, index)
        
        ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
        ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))
        STATE_CHOICES = [(c[0], c[1]) for c in EquipState.EQUIP_STATES]
        STATE_CHOICES.insert(0, ('', '-- choisir une action en premier --'))

        url1 = reverse('xhr_equip_state')
        url2 = reverse('xhr_equipment')
        url3 = reverse('xhr_station')

        form.fields['equip_action'].widget = forms.Select(choices=ACTION_CHOICES, attrs={'onchange': 'get_equip_state(this,\'' + url1 + '\',\'' + url2 + '\',\'' + url3 + '\');'})
        form.fields['equip_state'].widget = forms.Select(choices=STATE_CHOICES)

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return 

        Liste_equip = []

        # Obtain the information from the form needed for the validation
        intervention_station = self.instance.station
        intervention_date = self.instance.intervention_date

        # get forms that actually have valid data
        for form in self.forms:
            # Acquire data for each field
            if form.cleaned_data != {}:
                # Obtain the information from the formset needed for the validation
                if form.cleaned_data['equip_action']:
                    equip_action = form.cleaned_data['equip_action']
                if form.cleaned_data['equip_state']:
                    equip_state = form.cleaned_data['equip_state']
                if form.cleaned_data['equip']:
                    equip = form.cleaned_data['equip']
                    Liste_equip.append(equip)
                if form.cleaned_data['station']:
                    target_station = form.cleaned_data['station']

                #print "action : %s" % equip_action
                #print "state : %s" % equip_state
                #print "equip : %s" % equip
                #print "target_station : %s" % target_station

                #print "intervention_station : %s" % intervention_station
                #print "intervention_date : %s" % intervention_date

                #print "equip_last_place : %s" % equip_last_place(equip.id)
                #print "equip_place_todate : %s" % equip_place_todate(equip.id, intervention_date)

                #print "equip_last_state : %s" % EquipState.EQUIP_STATES[equip_last_state(equip.id)-1][1]
                #print "equip_state_todate : %s" % EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date)-1][1]

                # TODO vue de validation
                # Validation of equip_action and target state
                errors = 0

                if equip_action == EquipAction.ACHETER and equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.TESTER and (equip_state != EquipState.A_TESTER and equip_state != EquipState.DISPONIBLE and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.INSTALLER and equip_state != EquipState.OPERATION:
                    errors += 1
                if equip_action == EquipAction.DESINSTALLER and equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.CONSTATER_DEFAUT and (equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_PREV_DISTANTE and (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_CORR_DISTANTE and (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_PREV_SITE and (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_CORR_SITE and (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.EXPEDIER and equip_state != EquipState.EN_TRANSIT:
                    errors += 1
                if equip_action == EquipAction.RECEVOIR and equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.METTRE_HORS_USAGE and equip_state != EquipState.HORS_USAGE:
                    errors += 1
                if equip_action == EquipAction.CONSTATER_DISPARITION and equip_state != EquipState.DISPARU:
                    errors += 1
                if equip_action == EquipAction.RETROUVER and equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.METTRE_AU_REBUT and equip_state != EquipState.AU_REBUT:
                    errors += 1

                if errors != 0:  
                    raise forms.ValidationError('Etat final (%s) est invalide pour l\'action choisi  (%s)' % (EquipState.EQUIP_STATES[equip_state-1][1], EquipAction.EQUIP_ACTIONS[equip_action-1][1]))

                # TODO
                # Validation of equip_action and possible equip
                if equip_action == EquipAction.INSTALLER and equip_state_todate(equip.id, intervention_date) != EquipState.DISPONIBLE:
                     raise forms.ValidationError('Equipement (%s) non dans un etat disponible (%s) pour cet action (%s)' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date)-1][1], EquipAction.EQUIP_ACTIONS[equip_action-1][1]))

                if equip_action == EquipAction.RECEVOIR and equip_state_todate(equip.id, intervention_date) != EquipState.EN_TRANSIT:
                     raise forms.ValidationError('Equipement (%s) n\'est pas actuellement en transit (%s) pour reception' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date)-1][1]))

                # TODO
                # Validation of equip_action and last place
                errors = 0
                Actions = []
                Actions.append(EquipAction.TESTER)
                Actions.append(EquipAction.DESINSTALLER)
                Actions.append(EquipAction.CONSTATER_DEFAUT)
                Actions.append(EquipAction.MAINT_PREV_DISTANTE)
                Actions.append(EquipAction.MAINT_CORR_DISTANTE)
                Actions.append(EquipAction.MAINT_PREV_SITE)
                Actions.append(EquipAction.MAINT_CORR_SITE)
                Actions.append(EquipAction.METTRE_HORS_USAGE)

                for action in Actions:
                    if equip_action == action and equip_place_todate(equip.id, intervention_date) != intervention_station:
                        errors += 1

                if errors != 0:
                     raise forms.ValidationError('Equipement non present (%s) pour cette station (%s)' % (equip, intervention_station))

                # TODO
                # Validation of equip_action and target place
                errors = 0
                Actions = []
                Actions.append(EquipAction.TESTER)
                Actions.append(EquipAction.INSTALLER)
                Actions.append(EquipAction.CONSTATER_DEFAUT)
                Actions.append(EquipAction.MAINT_PREV_DISTANTE)
                Actions.append(EquipAction.MAINT_CORR_DISTANTE)
                Actions.append(EquipAction.MAINT_PREV_SITE)
                Actions.append(EquipAction.MAINT_CORR_SITE)
                Actions.append(EquipAction.RECEVOIR)
                Actions.append(EquipAction.METTRE_HORS_USAGE)
                Actions.append(EquipAction.RETROUVER)

                for action in Actions:
                    if equip_action == action and intervention_station != target_station:
                        errors += 1

                if errors != 0: 
                     raise forms.ValidationError('On doit effectuer cette action (%s) sur la station de l\'intervention (%s) et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], intervention_station, target_station))

                if equip_action == EquipAction.DESINSTALLER and target_station.site_type != StationSite.OBSERVATOIRE:
                     raise forms.ValidationError('On doit effectuer cette action (%s) et entreposer dans un OSU et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                if equip_action == EquipAction.EXPEDIER and (target_station.site_type != StationSite.OBSERVATOIRE and target_station.site_type != StationSite.SAV and target_station.site_type != StationSite.AUTRE):
                     raise forms.ValidationError('On doit effectuer cette action (%s) et expedier vers OSU, SAV ou Autre et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                if (equip_action == EquipAction.CONSTATER_DISPARITION or equip_action == EquipAction.METTRE_AU_REBUT) and target_station.site_type != StationSite.NEANT:
                     raise forms.ValidationError('On doit effectuer cette action (%s) et indiquer un lieu indetermine et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

        # Check that there is no more than one action per equip
        if not (len(set(Liste_equip)) == len(Liste_equip)):
            raise forms.ValidationError('On ne peut effectuer qu\'une seul action par equipement')

class IntervStationInlineFormset(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(IntervStationInlineFormset, self).add_fields(form, index)

        ACTION_CHOICES = [(c[0], c[1]) for c in StationAction.STATION_ACTIONS]
        ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))
        STATE_CHOICES = [(c[0], c[1]) for c in StationState.STATION_STATES]
        STATE_CHOICES.insert(0, ('', '-- choisir une action en premier --'))

        url = reverse('xhr_station_state')

        form.fields['station_action'].widget = forms.Select(choices=ACTION_CHOICES, attrs={'onchange': 'get_station_state(this,\'' + url + '\');'})
        form.fields['station_state'].widget = forms.Select(choices=STATE_CHOICES)

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return 

        # get forms that actually have valid data
        for form in self.forms:
            # Acquire data for each field
            if form.cleaned_data != {} and form.cleaned_data['station_action'] and form.cleaned_data['station_state']:
                station_action = form.cleaned_data['station_action']
                station_state = form.cleaned_data['station_state']

                # TODO vue de validation
                # Validation of station_action and final state
                errors = 0

                if station_action == StationAction.CREER and station_state != StationState.INSTALLATION:
                     errors += 1
                if station_action == StationAction.INSTALLER and station_state != StationState.INSTALLATION:
                     errors += 1
                if station_action == StationAction.OPERER and station_state != StationState.OPERATION:
                     errors += 1
                if station_action == StationAction.CONSTATER_DEFAUT and (station_state != StationState.DEFAUT or station_state != StationState.PANNE):
                     errors += 1
                if station_action == StationAction.MAINT_PREV_DISTANTE and (station_state != StationState.DEFAUT or station_state != StationState.PANNE or station_state != StationState.OPERATION):
                     errors += 1
                if station_action == StationAction.MAINT_CORR_DISTANTE and (station_state != StationState.DEFAUT or station_state != StationState.PANNE or station_state != StationState.OPERATION):
                     errors += 1
                if station_action == StationAction.MAINT_PREV_SITE and (station_state != StationState.DEFAUT or station_state != StationState.PANNE or station_state != StationState.OPERATION):
                     errors += 1
                if station_action == StationAction.MAINT_CORR_SITE and (station_state != StationState.DEFAUT or station_state != StationState.PANNE or station_state != StationState.OPERATION):
                     errors += 1
                if station_action == StationAction.DEMANTELER and station_state != StationState.FERMEE:
                     errors += 1

                if errors != 0:  
                     raise forms.ValidationError('Etat (%s) invalide pour l\'action choisi  (%s)' % (StationState.STATION_STATES[station_state-1][1], StationAction.STATION_ACTIONS[station_action-1][1]))
