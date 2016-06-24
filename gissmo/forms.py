# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
import time

from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import Group
from django.db.models import Q
from django.forms.widgets import CheckboxSelectMultiple
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

import autocomplete_light

from equipment import states as EquipState
from equipment import actions as EquipAction

from station import states as StationState
from station import actions as StationAction

from gissmo.models import (
    Organism,
    Built,
    Chain,
    Channel,
    ChannelCode,
    DataType,
    EquipDoc,
    EquipModel,
    EquipModelDoc,
    Equipment,
    ForbiddenEquipmentModel,
    IPAddress,
    Network,
    ParameterEquip,
    ParameterValue,
    StationDoc,
    StationSite,
)
from gissmo.views import (
    available_equip_state,
    available_equipment_scioper,
    available_station, available_built,
    equip_place_todate_id,
    equip_state_todate,
)
from gissmo.tools import timezone_aware
from gissmo.validators import validate_ipaddress


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

        args = [self.app_label, self.model_name, self.field_name, self.id]
        url = reverse('get_file', args=args)

        if value and hasattr(value, "url"):
            output.append(
                '%s <a target="_blank" href="%s">%s</a> <br />%s ' % (
                    'Currently:',
                    url,
                    value.name.split('/')[-1],
                    'Change:'))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class EquipModelDocInlineForm(forms.ModelForm):
    """
    Champ pour faire en sorte que les forms inline instanciées
    soient toujours avec un flag has_changed a True
    De cette facon si on change le supertype, type ou le modele du parent cela
    se repercute aux enfants
    """
    always_update = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        model = EquipModelDoc
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EquipModelDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['always_update'].initial = int(time.time())
            self.fields['document_equip_model'].widget = AdminFileWidget(
                attrs={
                    'app_label': instance_document._meta.app_label,
                    'model_name': instance_document._meta.object_name.lower(),
                    'field_name': 'document_equip_model',
                    'id': instance_document.id
                }
            )


class EquipDocInlineForm(forms.ModelForm):
    """
    Champ pour faire en sorte que les forms inline instanciées
    soient toujours avec un flag has_changed à True
    De cette façon si on change le supertype, type ou le modèle du parent cela
    se répercute aux enfants.
    """
    always_update = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    class Meta:
        model = EquipDoc
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(EquipDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['always_update'].initial = int(time.time())
            self.fields['document_equip'].widget = AdminFileWidget(
                attrs={
                    'app_label': instance_document._meta.app_label,
                    'model_name': instance_document._meta.object_name.lower(),
                    'field_name': 'document_equip',
                    'id': instance_document.id
                }
            )


class IntervDocInlineForm(forms.ModelForm):
    class Meta:
        model = EquipDoc
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(IntervDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['_file'].widget = AdminFileWidget(
                attrs={
                    'app_label': instance_document._meta.app_label,
                    'model_name': instance_document._meta.object_name.lower(),
                    'field_name': '_file',
                    'id': instance_document.id
                }
            )


class IPAddressInlineForm(forms.ModelForm):
    ip = forms.CharField(validators=[validate_ipaddress])

    class Meta:
        model = IPAddress
        fields = [
            "ip",
            "netmask"]


class InterventionForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(InterventionForm, self).__init__(*args, **kwargs)

        # today = datetime.now()
        # today_at_midnight = datetime(today.year, today.month, today.day)
        # self.fields['intervention_date'].initial = today_at_midnight
        # Hack to display time but let data empty to froce the user
        # to fill the field
        split_widget = widgets.AdminSplitDateTime()
        split_widget.widgets[0].attrs = {'class': 'vDateField', 'size': '10'}
        split_widget.widgets[1].attrs = {
            'class': 'vTimeField',
            'size': '8',
            'value': '00:00:00'
        }
        self.fields['intervention_date'].widget = split_widget


class EquipmentForm(autocomplete_light.ModelForm):
    """
    Add of fields to obtain the date of purchase and stockage_site only when
    it'a new equipment else hide the field and the label
    Only the site of type OBSERVATOIRE can be a storage place
    """
    observatories = StationSite.objects.filter(
        site_type=StationSite.OBSERVATOIRE
    )

    stockage_site = forms.ModelChoiceField(
        queryset=observatories,
        label="Storage place")

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['purchase_date'].widget = forms.HiddenInput()
            self.fields['purchase_date'].label = ""
            self.fields['stockage_site'].widget = forms.HiddenInput()
            self.fields['stockage_site'].label = ""
            self.fields['stockage_site'].required = False
        else:
            self.fields['purchase_date'].required = True
            self.fields['stockage_site'].required = True

        # initialization
        try:
            owner_default_value = Organism.objects.get(name='DT INSU')
        except (KeyError, Organism.DoesNotExist):
            owner_default_value = None

        self.fields['owner'].queryset = Organism.objects.filter(
            Q(_type=Organism.OBSERVATORY) |
            Q(_type=Organism.NETWORK) |
            Q(_type=Organism.UNKNOWN))
        self.fields['owner'].initial = owner_default_value
        self.fields['stockage_site'].queryset = \
            StationSite.objects.filter(site_type=StationSite.OBSERVATOIRE)

    class Meta:
        model = Equipment
        fields = "__all__"
        autocomplete_fields = ('equip_model')


class EquipModelForm(autocomplete_light.ModelForm):
    """
    Add autocomplete on equip_type field
    """
    class Meta:
        model = EquipModel
        fields = "__all__"
        autocomplete_fields = ('equip_type')


class ForbiddenEquipmentModelForm(autocomplete_light.ModelForm):
    """
    Add autocomplete on these fields:
      - original
      - recommended
    """
    class Meta:
        model = ForbiddenEquipmentModel
        fields = ['original', 'recommended']
        autocomplete_fields = ('original', 'recommended')


class StationDocInlineForm(forms.ModelForm):
    """
    """
    class Meta:
        model = StationDoc
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(StationDocInlineForm, self).__init__(*args, **kwargs)

        if 'instance' in kwargs:
            instance_document = kwargs['instance']
            self.fields['document_station'].widget = AdminFileWidget(
                attrs={
                    'app_label': instance_document._meta.app_label,
                    'model_name': instance_document._meta.object_name.lower(),
                    'field_name': 'document_station',
                    'id': instance_document.id})


class StationSiteForm(forms.ModelForm):
    """
    Add of a field to obtain the date of the creation and the associated
project only when it'a new station else hide the field and the label.
    """
    project = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Project',
        required=False)

    def __init__(self, *args, **kwargs):
        super(StationSiteForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['creation_date'].widget = forms.HiddenInput()
            self.fields['creation_date'].label = ""
            self.fields['project'].widget = forms.HiddenInput()
            self.fields['project'].label = ""
        else:
            self.fields['creation_date'].required = True
            self.fields['project'].required = True
            project_list = [g.id for g in self.current_user.groups.all()]
            self.fields['project'].queryset = \
                Group.objects.filter(id__in=project_list)
            if len(project_list) == 1:
                self.fields['project'].empty_label = None

        # intialization
        operator_default_value = None
        try:
            operator_default_value = Organism.objects.get(name='Unknown')
        except (KeyError, Organism.DoesNotExist):
            pass

        self.fields['operator'].queryset = Organism.objects.filter(
            Q(_type=Organism.OBSERVATORY) |
            Q(_type=Organism.NETWORK) |
            Q(_type=Organism.CUSTOMER_SERVICE) |
            Q(_type=Organism.UNKNOWN))
        self.fields['operator'].initial = operator_default_value

    class Meta:
        model = StationSite
        fields = "__all__"

    def clean(self):
        cleaned_data = super(StationSiteForm, self).clean()
        site_type = cleaned_data.get("site_type")
        latitude = cleaned_data.get("latitude")
        longitude = cleaned_data.get("longitude")
        elevation = cleaned_data.get("elevation")

        """
        Check that the latitude, longitude and elevation are filled for a
        station, test and theoric site
        """
        is_right_type = site_type in (
            StationSite.STATION,
            StationSite.SITE_TEST,
            StationSite.SITE_THEORIQUE)
        no_coordinates = \
            latitude is None or\
            longitude is None or\
            elevation is None
        if is_right_type and no_coordinates:
            raise forms.ValidationError(
                'Latitude, longitude and elevation are mandatory \
for this kind of site: %s' % dict(StationSite.SITE_CHOICES)[site_type])

        # Always return the full collection of cleaned data.
        return cleaned_data


class IntervUserInlineFormset(forms.models.BaseInlineFormSet):
    """
    Custom formset that support initial data.
    """

    def initial_form_count(self):
        """
        set 0 to use initial_extra explicitly.
        """
        if self.initial_extra:
            return 0
        else:
            return forms.models.BaseInlineFormSet.initial_form_count(self)

    def total_form_count(self):
        """
        use the initial_extra len to determine needed forms
        """
        if self.initial_extra:
            count = len(self.initial_extra) if self.initial_extra else 0
            count += self.extra
            return count
        else:
            return forms.models.BaseInlineFormSet.total_form_count(self)

    def clean(self):
        count = 0
        super(IntervUserInlineFormset, self).clean()
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data.get('DELETE', False):
                    continue
                count += 1
        if count < 1:
            raise forms.ValidationError('At least 1 operator!')


class IntervUserInlineForm(forms.models.ModelForm):
    """
    Custom model form that supports initial data when saved.
    """

    def has_changed(self):
        """
        Returns True if we have initial data.
        """
        has_changed = forms.models.ModelForm.has_changed(self)
        return bool(self.initial or has_changed)


class IntervEquipInlineForm(forms.models.ModelForm):
    """
    Custom model form that supports initial data when saved.
    """

    def has_changed(self):
        """
        Returns True if we have initial data.
        """
        has_changed = forms.models.ModelForm.has_changed(self)
        return bool(self.initial or has_changed)


class IntervEquipInlineFormset(forms.models.BaseInlineFormSet):

    def initial_form_count(self):
        """
        set 0 to use initial_extra explicitly.
        """
        if self.initial_extra:
            return 0
        else:
            return forms.models.BaseInlineFormSet.initial_form_count(self)

    def total_form_count(self):
        """
        use the initial_extra len to determine needed forms
        """
        if self.initial_extra:
            count = len(self.initial_extra) if self.initial_extra else 0
            count += self.extra
            return count
        else:
            return forms.models.BaseInlineFormSet.total_form_count(self)

    def add_fields(self, form, index):
        super(IntervEquipInlineFormset, self).add_fields(form, index)

        url1 = reverse('xhr_equip_state')
        url2 = reverse('xhr_equipment')
        url3 = reverse('xhr_station')
        url4 = reverse('xhr_built')

        STATE_CHOICES = []
        STATE_CHOICES.insert(0, ('', '-- Select a state --'))

        """
        Initialize form.fields
        """
        form.fields['equip'] = forms.ModelChoiceField(
            queryset=Equipment.objects.all().prefetch_related('equip_model'),
            empty_label="-- Select an equipment --",
            widget=forms.Select(
                attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}))

        form.fields['equip_state'].widget = forms.Select(choices=STATE_CHOICES)
        form.fields['station'] = forms.ModelChoiceField(
            queryset=StationSite.objects.all(),
            widget=forms.Select(
                attrs={'onchange': 'get_site_built(this,\'' + url4 + '\');'}),
            empty_label="-- Select a site --")
        form.fields['built'] = forms.ModelChoiceField(
            queryset=Built.objects.all(),
            empty_label="-- Select a place --",
            required=False)

        """
        Hack to check if the formset is already filled to present the complete
        list of actions else the list exclude the action of buying (Acheter).
        """

        if index is not None:
            """
            Obtain the value for each field of a line of a formset
            """
            action_id = form['equip_action'].value()
            equip_id = form['equip'].value()
            station_id = form['station'].value()
            # Not used (as flake8 said)
            # equip_state_id = form['equip_state'].value()
            # built_id = form['built'].value()

            try:
                intervention_station_id = self.instance.station.id
            except:
                intervention_station_id = station_id

            # intervention_station_id = self.instance.station.id
            # intervention_date = self.instance.intervention_date
            """
            06/08/2013 Add to keep the intervention number when we change the
            intervention date of an existing one.
            This trick permit us to exclude the intervention from the function
            equip_state_todate and equip_place_todate_id.
            We need this trick because the functions look in the DB for the
            status and place for a date before the change occur and if the
            date of the intervention change this interfere. Thus we have to
            exclude this from the query only if the date change.
            """
            # intervention_id = self.instance.id

            """
            All actions can be display
            """
            def value_is_1(the_id):
                try:
                    value = int(the_id)
                except:
                    value = None
                if value and value == 1:
                    return True
                return False

            if value_is_1(action_id):
                ACTION_CHOICES = [
                    (c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
                ACTION_CHOICES.insert(0, ('', '-- Select an action --'))
            else:
                """
                The BUY action is not display
                """
                # ACTION_CHOICES = [
                #     (c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS[1:]]
                """
                The BUY action is display
                """
                ACTION_CHOICES = [
                    (c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
                ACTION_CHOICES.insert(0, ('', '-- Select an action --'))

            ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- Select an action --'))

            """
            Filtering the queryset depending of the value
            """
            def is_not_empty(the_id):
                if the_id is not None and the_id != '':
                    return True
                return False
            if is_not_empty(action_id):
                form.fields['equip_state'].widget = \
                    forms.Select(choices=available_equip_state(action_id))
                if is_not_empty(intervention_station_id):
                    form.fields['station'] = forms.ModelChoiceField(
                        queryset=available_station(
                            action_id,
                            intervention_station_id),
                        widget=forms.Select(
                            attrs={
                                'onchange':
                                'get_site_built(this,\'' + url4 + '\');'
                            }),
                        empty_label=None)
                    if is_not_empty(equip_id):
                        form.fields['equip'] = forms.ModelChoiceField(
                            queryset=Equipment.objects.filter(pk=equip_id),
                            widget=forms.Select(
                                attrs={
                                    'onfocus':
                                        'get_equip(this,\'' + url2 + '\');'}),
                            empty_label=None)
                    """
                    The queryset of the equip field is not filtering because
                    we trap the focus event on that field.
                    if intervention_date != None and intervention_date != '':
                        Permit the empty label because if the date of the
                        intervention change the available_equipment can return
                        to the queryset choices without the ancient value.
                        form.fields['equip'] = forms.ModelChoiceField(
                        queryset = available_equipment(
                        action_id, intervention_station_id, intervention_date,
                        intervention_id), widget=forms.Select(
                        attrs={'onfocus':
                        'get_equip(this,\'' + url2 + '\');'}))
                        #form.fields['equip'] = forms.ModelChoiceField(
                        queryset = available_equipment(
                        action_id, intervention_station_id,
                        intervention_date, intervention_id))
                    """

            if is_not_empty(station_id):
                form.fields['built'] = forms.ModelChoiceField(
                    queryset=available_built(station_id),
                    required=False)

        else:
            """
            The BUY action permitted
            """
            ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- Select an action --'))

            """
            Special case if we came from a specific equipment
            """
            form.fields['equip'] = forms.ModelChoiceField(
                queryset=Equipment.objects.none(),
                empty_label="-- Select an equipment --",
                widget=forms.Select(
                    attrs={
                        'onfocus': 'get_equip(this,\'' + url2 + '\');'}))

        form.fields['equip_action'].widget = forms.Select(
            choices=ACTION_CHOICES,
            attrs={
                'onchange':
                'get_equip_state(this,\'' + url1 +
                    '\',\'' + url2 +
                    '\',\'' + url3 +
                    '\',\'' + url4 +
                    '\');'})

    def clean(self):

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on
            # its own
            return

        Liste_equip = []

        # Obtain the information from the form needed for the validation
        intervention_station_id = self.data.get('station')
        intervention_id = self.instance.id

        # Check if intervention_id is set to something else put the value 0
        if not intervention_id:
            intervention_id = 0

        if intervention_station_id:
            try:
                intervention_station = StationSite.objects.get(
                    id=intervention_station_id)
            except StationSite.DoesNotExist:
                intervention_station = StationSite.objects.none()
        else:
            intervention_station = StationSite.objects.none()

        date_intervention = self.data.get('intervention_date_0')
        heure_intervention = self.data.get('intervention_date_1')
        if date_intervention and heure_intervention:
            date_heure_intervention = u''.join(
                [date_intervention, u' ', heure_intervention])
            try:
                naive_datetime = datetime.strptime(
                    date_heure_intervention,
                    "%Y-%m-%d %H:%M:%S")
                intervention_date = timezone_aware(naive_datetime)
            except ValueError:
                intervention_date = ''
            pass
        else:
            intervention_date = ''

        # get forms that actually have valid data
        for form in self.forms:
            # Acquire data for each field
            if form.cleaned_data != {}:
                # Obtain the information from the formset needed for the
                # validation
                equip_action = ''
                equip_state = ''
                equip = ''
                target_station = ''
                if form.cleaned_data['equip_action']:
                    equip_action = form.cleaned_data['equip_action']
                if form.cleaned_data['equip_state']:
                    equip_state = form.cleaned_data['equip_state']
                if form.cleaned_data['equip']:
                    equip = form.cleaned_data['equip']
                    Liste_equip.append(equip)
                if form.cleaned_data['station']:
                    target_station = form.cleaned_data['station']

                """
                Validation of equip_action and possible equipment
                We do the action only for the equipment on the site
                """
                errors = 0
                Actions = []
                Actions.append(EquipAction.TESTER)
                Actions.append(EquipAction.DESINSTALLER)
                Actions.append(EquipAction.CONSTATER_DEFAUT)
                Actions.append(EquipAction.MAINT_PREV_DISTANTE)
                Actions.append(EquipAction.MAINT_CORR_DISTANTE)
                Actions.append(EquipAction.MAINT_PREV_SITE)
                Actions.append(EquipAction.MAINT_CORR_SITE)
                Actions.append(EquipAction.EXPEDIER)
                Actions.append(EquipAction.METTRE_HORS_USAGE)
                Actions.append(EquipAction.CONSTATER_DISPARITION)
                Actions.append(EquipAction.METTRE_AU_REBUT)

                for action in Actions:
                    same_action = equip_action == action
                    todateid = equip_place_todate_id(
                        equip.id,
                        intervention_date,
                        int(intervention_id))
                    sameintervention = todateid == int(intervention_station_id)
                    if same_action and not sameintervention:
                        errors += 1

                if errors != 0:
                    raise forms.ValidationError(
                        '%s equipment not present for this station: (%s)' %
                        (equip, intervention_station))

                """
                The action TESTER is valid only if the status were OPERATION,
                A_TESTER, DISPONIBLE, DEFAUT, PANNE or AUTRE before.
                """
                if equip_action == EquipAction.TESTER and (
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.OPERATION and
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.A_TESTER and
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.DISPONIBLE and
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.DEFAUT and
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.PANNE and
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.AUTRE):
                    raise forms.ValidationError(
                        "Disallowed action '%s' for equipment '%s' \
(state: %s)" % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            equip,
                            EquipState.EQUIP_STATES[equip_state_todate(
                                equip.id,
                                intervention_date,
                                int(intervention_id)) - 1][1]))

                """
                The action INSTALLER is valid only if the status was DISPONIBLE
                before.
                """
                if equip_action == EquipAction.INSTALLER and \
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.DISPONIBLE:
                    raise forms.ValidationError(
                        "Equipement '%s' should be available (%s instead) \
for this action: %s" % (
                            equip,
                            EquipState.EQUIP_STATES[equip_state_todate(
                                equip.id,
                                intervention_date,
                                int(intervention_id)) - 1][1],
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1]))

                """
                The action RECEVOIR is valid only if the status was EN_TRANSIT
                before.
                """
                if equip_action == EquipAction.RECEVOIR and \
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.EN_TRANSIT:
                    raise forms.ValidationError(
                        "Equipement '%s' should be in transit \
(% instead)" % (
                            equip,
                            EquipState.EQUIP_STATES[equip_state_todate(
                                equip.id,
                                intervention_date,
                                int(intervention_id)) - 1][1]))

                """
                The action RETROUVER is valid only if the status was DISPARU
                before.
                """
                if equip_action == EquipAction.RETROUVER and \
                    equip_state_todate(
                        equip.id,
                        intervention_date,
                        int(intervention_id)) != EquipState.DISPARU:
                    raise forms.ValidationError(
                        "Equipement '%s' not lost (%s instead)" % (
                            equip, EquipState.EQUIP_STATES[equip_state_todate(
                                equip.id,
                                intervention_date,
                                int(intervention_id)) - 1][1]))
                """
                The action MAINT_CORR_DISTANTE or MAINT_CORR_SITE is valid only
                if the status was DEFAUT or PANNE before.
                """
                authorized_actions = [
                    EquipAction.MAINT_CORR_DISTANTE,
                    EquipAction.MAINT_CORR_SITE]
                unauthorized_states = [
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                latest_equip_state = equip_state_todate(
                    equip.id,
                    intervention_date,
                    int(intervention_id))
                action_allowed = equip_action in authorized_actions
                equip_state_ok = latest_equip_state not in unauthorized_states
                if action_allowed and equip_state_ok:
                    raise forms.ValidationError(
                        "Equipement '%s' should be either in failure or \
broken (%s instead)" % (
                            equip,
                            EquipState.EQUIP_STATES[equip_state_todate(
                                equip.id,
                                intervention_date,
                                int(intervention_id)) - 1][1]))

                # TODO vue de validation
                # Validation of equip_action and target status
                errors = 0

                unallowed_tester_states = [
                    EquipState.OPERATION,
                    EquipState.A_TESTER,
                    EquipState.DISPONIBLE,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                is_acheter = equip_action == EquipAction.ACHETER
                is_tester = equip_action == EquipAction.TESTER

                if is_acheter and equip_state != EquipState.A_TESTER:
                    errors += 1
                if is_tester and equip_state not in unallowed_tester_states:
                    errors += 1

                is_install = equip_action == EquipAction.INSTALLER
                unallowed_install_states = [
                    EquipState.OPERATION,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_install and equip_state not in unallowed_install_states:
                    errors += 1

                is_desinstall = equip_action == EquipAction.DESINSTALLER
                unallowed_desinstall_states = [
                    EquipState.A_TESTER,
                    EquipState.DISPONIBLE,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_desinstall and \
                        equip_state not in unallowed_desinstall_states:
                    errors += 1

                is_constat = equip_action == EquipAction.CONSTATER_DEFAUT
                unallowed_constat_states = [
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_constat and equip_state not in unallowed_constat_states:
                    errors += 1

                is_prev_distante = \
                    equip_action == EquipAction.MAINT_PREV_DISTANTE
                unallowed_prev_distante_states = [
                    EquipState.OPERATION,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_prev_distante and \
                        equip_state not in unallowed_prev_distante_states:
                    errors += 1

                is_corr_distante = \
                    equip_action == EquipAction.MAINT_CORR_DISTANTE
                unallowed_corr_distante_states = [
                    EquipState.OPERATION,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_corr_distante and \
                        equip_state not in unallowed_corr_distante_states:
                    errors += 1

                is_prev_site = equip_action == EquipAction.MAINT_PREV_SITE
                unallowed_prev_site_states = [
                    EquipState.DISPONIBLE,
                    EquipState.OPERATION,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_prev_site and \
                        equip_state not in unallowed_prev_site_states:
                    errors += 1

                is_corr_site = equip_action == EquipAction.MAINT_CORR_SITE
                unallowed_corr_site_states = [
                    EquipState.DISPONIBLE,
                    EquipState.OPERATION,
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if is_corr_site and \
                        equip_state not in unallowed_corr_site_states:
                    errors += 1

                is_expedier = equip_action == EquipAction.EXPEDIER
                if is_expedier and equip_state != EquipState.EN_TRANSIT:
                    errors += 1

                is_recevoir = equip_action == EquipAction.RECEVOIR
                unallowed_recevoir = [
                    EquipState.A_TESTER,
                    EquipState.DISPONIBLE]
                if is_recevoir and equip_state not in unallowed_recevoir:
                    errors += 1

                is_hors_usage = equip_action == EquipAction.METTRE_HORS_USAGE
                if is_hors_usage and equip_state != EquipState.HORS_USAGE:
                    errors += 1

                is_disparu = equip_action == EquipAction.CONSTATER_DISPARITION
                if is_disparu and equip_state != EquipState.DISPARU:
                    errors += 1

                is_retrouver = equip_action == EquipAction.RETROUVER
                if is_retrouver and equip_state != EquipState.A_TESTER:
                    errors += 1

                is_rebut = equip_action == EquipAction.METTRE_AU_REBUT
                if is_rebut and equip_state != EquipState.AU_REBUT:
                    errors += 1

                if errors != 0:
                    raise forms.ValidationError(
                        "Invalid final status (%s) for action: %s" % (
                            EquipState.EQUIP_STATES[equip_state - 1][1],
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1]))

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
                    same_action = equip_action == action
                    if same_action and intervention_station != target_station:
                        errors += 1

                if errors != 0:
                    raise forms.ValidationError(
                        'Given action (%s) should be made on intervention \
site (%s) instead of: %s' % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            intervention_station, target_station))

                # The action DESINSTALLER is valid only if the target_station
                # is an OSU
                is_desinstall = equip_action == EquipAction.DESINSTALLER
                is_observatoire = \
                    target_station.site_type == StationSite.OBSERVATOIRE
                if is_desinstall and not is_observatoire:
                    raise forms.ValidationError(
                        'Given action (%s) should be done. Then stock in an \
 OSU and not in: %s' % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            target_station))

                # The action EXPEDIER is valid only if the target_station is
                # an OSU or SAV or AUTRE
                is_expedier = equip_action == EquipAction.EXPEDIER
                type_site = target_station.site_type
                unallowed_sites = [
                    StationSite.OBSERVATOIRE,
                    StationSite.SAV,
                    StationSite.AUTRE]
                if is_expedier and type_site not in unallowed_sites:
                    raise forms.ValidationError(
                        "Given action (%s) should be done. Then send it \
either to an OSU or a customer service or 'Other', it should not be: %s" % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            target_station))

                # The actions CONSTATER_DISPARITION and METTRE_AU_REBUT are
                # valid only if the target_station is NEANT
                is_disparu = equip_action == EquipAction.CONSTATER_DISPARITION
                is_rebut = equip_action == EquipAction.METTRE_AU_REBUT
                site_is_neant = target_station.site_type
                if (is_disparu or is_rebut) and not site_is_neant:
                    raise forms.ValidationError(
                        'You should apply this action (%s). Then add an \
%s place. Not this one: %s' % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            StationSite.NEANT,
                            target_station))

                # The action ACHETER is valid only if the target_station is an
                # OSU.
                is_acheter = equip_action == EquipAction.ACHETER
                site_is_observatoire = \
                    target_station.site_type == StationSite.OBSERVATOIRE
                if is_acheter and not site_is_observatoire:
                    raise forms.ValidationError(
                        "Given action (%s) should be done. Then indicate an \
OSU. Not this one: %s" % (
                            EquipAction.EQUIP_ACTIONS[equip_action - 1][1],
                            target_station))

                # The status DISPONIBLE is valid only if the target_station is
                # an OSU.
                is_disponible = equip_state == EquipState.DISPONIBLE
                type_site = target_station.site_type
                unallowed_sites = [
                    StationSite.OBSERVATOIRE,
                    StationSite.STATION,
                    StationSite.SITE_TEST]
                if is_disponible and type_site not in unallowed_sites:
                    raise forms.ValidationError(
                        "%s equipement should be only in either one station \
or an OSU. Not this one: %s" % (
                            EquipState.EQUIP_STATES[equip_state - 1][1],
                            target_station))

                # The status OPERATION is valid only if the target_station is
                # an STATION_SISMOLOGIQUE.
                is_operation = equip_state == EquipState.OPERATION
                if is_operation and (
                        target_station.site_type != StationSite.STATION and
                        target_station.site_type != StationSite.SITE_TEST):
                    raise forms.ValidationError(
                        '%s equipement should be only in one station. Not \
this one: %s' % (
                            EquipState.EQUIP_STATES[equip_state - 1][1],
                            target_station))

        # Check that there is no more than one action per equip
        if not (len(set(Liste_equip)) == len(Liste_equip)):
            raise forms.ValidationError(
                'Only one action per equipment!')


class IntervStationInlineFormset(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(IntervStationInlineFormset, self).add_fields(form, index)

        """
        Hack to check if the formset is already filled
        to present the complete list of actions
        else the list exclude the action of creating (Creer code station)
        """
        if index:
            ACTION_CHOICES = [
                (c[0], c[1]) for c in StationAction.STATION_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- Select an action --'))
        else:
            ACTION_CHOICES = [
                (c[0], c[1]) for c in StationAction.STATION_ACTIONS[1:]]
            ACTION_CHOICES.insert(0, ('', '-- select an action --'))

        STATE_CHOICES = [(c[0], c[1]) for c in StationState.STATION_STATES]
        STATE_CHOICES.insert(0, ('', '-- first select an action --'))

        url = reverse('xhr_station_state')

        form.fields['station_action'].widget = forms.Select(
            choices=ACTION_CHOICES,
            attrs={'onchange': 'get_station_state(this,\'' + url + '\');'})
        form.fields['station_state'].widget = forms.Select(
            choices=STATE_CHOICES)

    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on
            # its own.
            return

        # get forms that actually have valid data
        for form in self.forms:
            # Acquire data for each field
            is_dict = isinstance(form.cleaned_data, dict)
            if not is_dict:
                continue
            d_action = 'station_action' in form.cleaned_data
            d_state = 'station_state' in form.cleaned_data
            if any(form.cleaned_data) and d_action and d_state:
                station_action = form.cleaned_data['station_action']
                station_state = form.cleaned_data['station_state']

                # TODO vue de validation
                # Validation of station_action and final status
                errors = 0

                s_action = station_action
                is_creer = s_action == StationAction.CREER
                is_installer = s_action == StationAction.INSTALLER
                is_operer = s_action == StationAction.OPERER
                is_defaut = s_action == StationAction.CONSTATER_DEFAUT
                is_prev_dist = s_action == StationAction.MAINT_PREV_DISTANTE
                is_corr_dist = s_action == StationAction.MAINT_CORR_DISTANTE
                is_prev_site = s_action == StationAction.MAINT_PREV_SITE
                is_corr_site = s_action == StationAction.MAINT_CORR_SITE
                is_demanteler = s_action == StationAction.DEMANTELER
                unallowed_defaut_states = [
                    StationState.DEFAUT,
                    StationState.PANNE]
                unallowed_prev_dist_states = [
                    StationState.DEFAUT,
                    StationState.PANNE,
                    StationState.OPERATION]
                unallowed_corr_dist_states = [
                    StationState.DEFAUT,
                    StationState.PANNE,
                    StationState.OPERATION]
                unallowed_prev_site_states = [
                    StationState.DEFAUT,
                    StationState.PANNE,
                    StationState.OPERATION]
                unallowed_corr_site_states = [
                    StationState.DEFAUT,
                    StationState.PANNE,
                    StationState.OPERATION]
                if is_creer and station_state != StationState.INSTALLATION:
                    errors += 1
                if is_installer and station_state != StationState.INSTALLATION:
                    errors += 1
                if is_operer and station_state != StationState.OPERATION:
                    errors += 1
                if is_defaut and station_state not in unallowed_defaut_states:
                    errors += 1
                if is_prev_dist and \
                        station_state not in unallowed_prev_dist_states:
                    errors += 1
                if is_corr_dist and \
                        station_state not in unallowed_corr_dist_states:
                    errors += 1
                if is_prev_site and \
                        station_state not in unallowed_prev_site_states:
                    errors += 1
                if is_corr_site and \
                        station_state not in unallowed_corr_site_states:
                    errors += 1
                if is_demanteler and station_state != StationState.FERMEE:
                    errors += 1

                if errors != 0:
                    raise forms.ValidationError(
                        'Invalid status (%s) for given action (%s)' %
                        (
                            StationState.STATION_STATES[
                                station_state - 1][1],
                            StationAction.STATION_ACTIONS[
                                station_action - 1][1])
                    )


class ChainInlineFormset(forms.models.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        """
        Grabs the curried initial values and stores them into a 'private'
        variable. Note: the use of self.__initial is important, using
        self.initial or self._initial will be erased by a parent class
        """
        self.__initial = kwargs.pop('initial', [])
        super(ChainInlineFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(ChainInlineFormset, self).add_fields(form, index)

        # TODO Ameliorer cette comparaison
        if self.__initial and self.__initial != ['']:
            # Flake8 consider this variable 'station' unused.
            # TODO: probably that station was used to filter equipment by
            # last station (with last_station_id)
            # station = get_object_or_404(StationSite, id=self.__initial[0])
            form.fields['equip'] = forms.ModelChoiceField(
                queryset=Equipment.objects.all())

        url = reverse('xhr_equip_oper')

        """
        Initialize form.fields
        """
        ORDER_CHOICES = [(c[0], c[1]) for c in Chain.ORDER_CHOICES]
        ORDER_CHOICES.insert(0, ('', '-- Select a type --'))

        form.fields['equip'] = forms.ModelChoiceField(
            queryset=Equipment.objects.all().prefetch_related('equip_model'),
            empty_label="-- Select a type --")
        form.fields['order'].widget = forms.Select(
            choices=ORDER_CHOICES,
            attrs={'onchange': 'get_equip_oper(this,\'' + url + '\');'})

        if index is not None:
            try:
                channel_station_id = self.instance.station_id
                channel_date = self.instance.start_date
                form.fields['equip'] = forms.ModelChoiceField(
                    queryset=available_equipment_scioper(
                        channel_station_id,
                        channel_date),
                    empty_label=None)
            except:
                return


class ChannelForm(forms.ModelForm):
    """
    Obtain the latitude, longitude and elevation of the station
    the first time we add channel via the site form
    """

    class Meta:
        model = Channel
        fields = "__all__"

    # Hack field to show only if channel code and sample rate not fit
    accept_anyway = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)

        # Hack to simulate warning message via raise Validationerror
        if "accept_anyway" in self.errors:
            self.fields['accept_anyway'].widget = forms.CheckboxInput()
        else:
            self.fields['accept_anyway'].widget = forms.HiddenInput()
            self.fields['accept_anyway'].label = ""

        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'station' in initial:
                station = get_object_or_404(StationSite, id=initial['station'])
                self.fields['latitude'].initial = station.latitude
                self.fields['longitude'].initial = station.longitude
                self.fields['elevation'].initial = station.elevation
                self.fields['station'].initial = station.id

        # Flake8 consider 'url' as not used
        # url = reverse('xhr_station_position')

        self.fields['depth'].initial = '0'
        split_widget = widgets.AdminSplitDateTime()
        split_widget.widgets[0].attrs = {'class': 'vDateField', 'size': '10'}
        split_widget.widgets[1].attrs = {
            'class': 'vTimeField',
            'size': '8',
            'value': '00:00:00'}
        self.fields['start_date'].widget = split_widget
        self.fields['location_code'].initial = '00'
        self.fields['location_code'].required = False

        """
        CHANNEL_CHOICES = [
            ('', '---'),('BHE','BHE'),('BHN','BHN'),('BHZ','BHZ'), \
            ('CHE','CHE'),('CHN','CHN'),('CHZ','CHZ'), \
            ('DPE','DPE'),('DPN','DPN'),('DPZ','DPZ'), \
            ('EHE','EHE'),('EHN','EHN'),('EHZ','EHZ'), \
            ('ELE','ELE'),('ELN','ELN'),('ELZ','ELZ'), \
            ('HHE','HHE'),('HHN','HHN'),('HHZ','HHZ'), \
            ('LHE','LHE'),('LHN','LHN'),('LHZ','LHZ'), \
            ('SHE','SHE'),('SHN','SHN'),('SHZ','SHZ'), \
            ('VHE','VHE'),('VHN','VHN'),('VHZ','VHZ'), \
            ('LDI','LDI'),('LII','LII'),('LKI','LKI'), \
            ('HNE','HNE'),('HNN','HNN'),('HNZ','HNZ'), \
            ('BH1','BH1'),('BH2','BH2'), \
            ('LH1','LH1'),('LH2','LH2'), \
            ('VH1','VH1'),('VH2','VH2'), \
            ('HN2','HN2'),('HN3','HN3'),]
        """
        channels = ChannelCode.objects.all().order_by('presentation_rank')
        self.fields['channel_code'] = forms.ModelChoiceField(
            queryset=channels,
            widget=forms.Select(
                attrs={'onchange': 'get_dip_azimut_value(this);'}),
            empty_label='--')
        self.fields['station'] = forms.ModelChoiceField(
            queryset=StationSite.objects.all())
        self.fields["data_type"].widget = CheckboxSelectMultiple()
        self.fields["data_type"].queryset = DataType.objects.all()
        self.fields["data_type"].initial = \
            [t.pk for t in DataType.objects.filter(
                Q(type_description='CONTINUOUS') |
                Q(type_description='GEOPHYSICAL'))]

    def clean(self):
        cleaned_data = super(ChannelForm, self).clean()
        channel_code = cleaned_data.get("channel_code")
        rate = cleaned_data.get("sample_rate")
        accept = cleaned_data.get("accept_anyway")

        # If accept is checked, no check needed
        if accept:
            return cleaned_data
        # Check that the sample rate fit in the range for the channel code
        # We can bypass this validation with the accept field
        # http://www.iris.edu/manuals/SEED_appA.htm
        if channel_code and channel_code.channel_code and \
                rate is not None:
            code = channel_code.channel_code[0]
            d_fail = code == 'D' and not(rate >= 250 and rate < 1000)
            c_fail = code == 'C' and not(rate >= 250 and rate < 1000)
            e_fail = code == 'E' and not(rate >= 80 and rate < 250)
            s_fail = code == 'S' and not(rate >= 10 and rate < 80)
            h_fail = code == 'H' and not(rate >= 80)
            b_fail = code == 'B' and not(rate >= 10 and rate < 80)
            m_fail = code == 'M' and not(rate > 1 and rate < 10)
            l_fail = code == 'L' and not(rate == 1)
            v_fail = code == 'V' and not(rate == 0.1)
            u_fail = code == 'U' and not(rate == 0.01)
            if any(
                [
                    d_fail,
                    c_fail,
                    e_fail,
                    s_fail,
                    h_fail,
                    b_fail,
                    m_fail,
                    l_fail,
                    v_fail,
                    u_fail]):
                self.add_error('sample_rate', "Sample rate unexpected.")
                self.add_error('accept_anyway', "Bypass error.")
                raise forms.ValidationError(
                    'Sample rate (%s) not in the range for this channel \
code (%s)' % (rate, channel_code.channel_code))
        # Always return the full collection of cleaned data.
        return cleaned_data


class ChainConfigInlineFormset(forms.models.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(ChainConfigInlineFormset, self).add_fields(form, index)

        url1 = reverse('xhr_parameter_value')
        model_id = self.instance.equip.equip_model.id

        query = ParameterEquip.objects.filter(
            equip_model_id=model_id).prefetch_related(
                'equip_model')
        form.fields['parameter'] = forms.ModelChoiceField(
            queryset=query,
            widget=forms.Select(
                attrs={
                    'onchange':
                    'get_parameter_value(this,\'' + url1 + '\', \'chainconfig\');'}))
        form.fields['value'] = forms.ModelChoiceField(
            queryset=ParameterValue.objects.all(),
            widget=forms.Select(
                attrs={
                    'onfocus': 'get_parameter_value(this,\'' + url1 + '\', \'chainconfig\');'}),
            empty_label="-- Select a parameter --")


class ChannelChainInlineFormset(forms.models.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(ChannelChainInlineFormset, self).add_fields(form, index)

        if index is not None:
            """
            Obtain the value for each field of a line of a formset
            """
            parameter_id = form['parameter'].value()

            form.fields['parameter'] = forms.ModelChoiceField(
                queryset=ParameterEquip.objects.filter(
                    pk=parameter_id).prefetch_related(
                        'equip_model'),
                empty_label=None)
            form.fields['value'] = forms.ModelChoiceField(
                queryset=ParameterValue.objects.filter(
                    parameter_id=parameter_id),
                empty_label=None)


class ConfigEquipInlineFormset(forms.models.BaseInlineFormSet):
    """
    Custom formset to filter parameters and value.
    """

    def add_fields(self, form, index):
        super(ConfigEquipInlineFormset, self).add_fields(form, index)
        if self.instance:
            url1 = reverse('xhr_parameter_value')
            qs_params = ParameterEquip.objects.filter(
                equip_model_id=self.instance.equip_model_id)

            form.fields['parameter'] = forms.ModelChoiceField(
                queryset=qs_params.prefetch_related('equip_model'),
                widget=forms.Select(
                    attrs={
                        'onchange':
                            'get_parameter_value(this,\'' + url1 + '\', \'configequip\');'}))
            form.fields['value'] = forms.ModelChoiceField(
                queryset=ParameterValue.objects.filter(
                    parameter_id__in=[x.id for x in qs_params]),
                widget=forms.Select(
                    attrs={
                        'onfocus':
                            'get_parameter_value(this,\'' + url1 + '\', \'configequip\');'}),
                empty_label="-- Select a parameter --")


class CreateChannelForm(forms.Form):
    BH = 'BH'
    CH = 'CH'
    DP = 'DP'
    EH = 'EH'
    EL = 'EL'
    HH = 'HH'
    HN = 'HN'
    LH = 'LH'
    MH = 'MH'
    SH = 'SH'
    UH = 'UH'
    VH = 'VH'

    CHOICES = (
        (BH, BH),
        (CH, CH),
        (DP, DP),
        (EH, EH),
        (EL, EL),
        (HH, HH),
        (HN, HN),
        (LH, LH),
        (MH, MH),
        (SH, SH),
        (UH, UH),
        (VH, VH),
    )
    code = forms.ChoiceField(
        choices=CHOICES,
        label='Starting code',
        required=True,
        widget=forms.Select(
            attrs={
                'onchange': 'set_sample_rate(this);'}))
    network = forms.ChoiceField(
        choices=[(x.id, x.network_code) for x in Network.objects.all()],
        label='Network',
        required=True)
    location = forms.CharField(
        max_length=2,
        label='Location code',
        initial='00',
        required=True)
    date = forms.SplitDateTimeField(
        label='Starting date (yyyy-mm-dd)',
        widget=widgets.AdminSplitDateTime,
        required=True)
    rate = forms.FloatField(
        label='Sample rate',
        required=True)

    def __init__(self, *args, **kwargs):
        super(CreateChannelForm, self).__init__(*args, **kwargs)

        if 'instance' not in kwargs:
            choices = self.fields['code'].choices
            if not choices:
                return
            try:
                first_letter = choices[0][0][0]
            except Exception:
                return
            bandcode_values = {
                'B': 20,
                'H': 100,
                'L': 1,
                'V': 0.1,
                'U': 0.01,
                'E': 100,
                'S': 50,
                'M': 5,
                'D': 500,
                'C': 500,
            }
            self.fields['rate'].initial = bandcode_values[first_letter]

    def clean(self):
        cleaned_data = super(CreateChannelForm, self).clean()
        code = cleaned_data.get('code', None)
        rate = cleaned_data.get('rate', None)

        # As code and rate are required, continue each field validation
        if not code or not rate:
            return

        # Band code found in Appendix A from SEED manual, v.2.4
        sample_rate_bandcode = {
            'B': [9, 80],  # >= 10 and < 80
            'C': [249, 1000],  # >= 250 and < 1000
            'D': [249, 1000],  # >= 250 and < 1000
            'E': [79, 250],  # >= 80 and < 250
            'H': [79, 250],  # >= 80 and < 250
            'L': [0.1, 1.1],  # ≈ 1
            'M': [1, 10],  # > 1 and < 10
            'S': [9, 80],  # >= 10 and < 80
            'U': [0.001, 0.1],  # ≈ 0.01
            'V': [0.01, 1],  # ≈ 0.1
        }

        code_first_letter = code[0]
        # First letter not found
        if code_first_letter not in sample_rate_bandcode:
            raise forms.ValidationError(
                "Band code not implemented!",
                code="invalid")

        # Check band code range
        bandcode_range = sample_rate_bandcode[code_first_letter]
        if rate <= bandcode_range[0] or rate >= bandcode_range[1]:
            raise forms.ValidationError(
                "Sample rate should be > %(min)s and < %(max)s",
                code='invalid',
                params={
                    'min': bandcode_range[0],
                    'max': bandcode_range[1]})
