# coding=utf-8

from datetime import datetime
import time

from django import forms
from django.contrib.admin import widgets
from django.contrib.auth.models import User
from django.db.models import Q
from django.forms.widgets import CheckboxSelectMultiple
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from gissmo.models import Actor, EquipModelDoc, Equipment, EquipDoc, StationSite, \
    StationDoc, Chain, Channel, Built, DataType, EquipSupertype, Project, \
    ProjectUser, ParameterEquip, ParameterValue
from gissmo.views import equip_state_todate, equip_place_todate_id, \
    available_equip_state, available_station, available_built, \
    available_equipment_scioper
from gissmo.models import EquipAction, EquipState, StationAction, StationState, \
    ChannelCode
from gissmo.tools import timezone_aware


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
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), url, value.name.split('/')[-1], _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class ActorForm(forms.ModelForm):

    class Meta:
        model = Actor
        fields = "__all__"

    def clean(self):
        cleaned_data = super(ActorForm, self).clean()
        name = cleaned_data.get("actor_name")

        # Check that an authenticated user via Auth.user will not change is
        # actor_name in the Actor table
        # The name is use for the default actor in intervention
        #
        # Check that the actor_name Inconnu will not change too
        # The name is use for the default operator in site creation

        if self.instance.id:
            actor = get_object_or_404(Actor, id=self.instance.id)
            if User.objects.filter(username=actor.actor_name).exists():
                if actor.actor_name != name:
                    raise forms.ValidationError('The name for this actor must stay : %s' % actor.actor_name)
            elif actor.actor_name == 'Inconnu' and name != 'Inconnu':
                raise forms.ValidationError('The name for this actor must stay : Inconnu')

        # Always return the full collection of cleaned data.
        return cleaned_data


class EquipModelDocInlineForm(forms.ModelForm):
    """
    Champ pour faire en sorte que les forms inline instancier
    soit toujours avec un flag has_changed a True
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
    Champ pour faire en sorte que les forms inline instancier
    soit toujours avec un flag has_changed a True
    De cette facon si on change le supertype, type ou le modele du parent cela
    se repercute aux enfants
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

class EquipmentForm(forms.ModelForm):
    """
    Add of fields to obtain the date of purchase and stockage_site only when
    it'a new equipment else hide the field and the label
    Only the site of type OBSERVATOIRE can be a stockage site
    """
    observatories = StationSite.objects.filter(
        site_type=StationSite.OBSERVATOIRE
    )

    purchase_date = forms.DateField(
        widget=widgets.AdminDateWidget,
        label='Date achat',
        required=False
    )

    stockage_site = forms.ModelChoiceField(queryset=observatories)

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

        # initialization
        try:
            owner_default_value = Actor.objects.get(actor_name='DT INSU')
        except (KeyError, Actor.DoesNotExist):
            owner_default_value = None

        self.fields['owner'].queryset = Actor.objects.filter(Q(actor_type=Actor.OBSERVATOIRE) | Q(actor_type=Actor.ORGANISME) | Q(actor_type=Actor.INCONNU))
        self.fields['owner'].initial = owner_default_value
        self.fields['equip_supertype'].queryset = EquipSupertype.objects.all().order_by('presentation_rank')
        self.fields['stockage_site'].queryset = StationSite.objects.filter(site_type=StationSite.OBSERVATOIRE)

    class Meta:
        model = Equipment
        fields = "__all__"


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
            self.fields['document_station'].widget = AdminFileWidget(attrs={'app_label':instance_document._meta.app_label, 'model_name':instance_document._meta.object_name.lower(), 'field_name':'document_station', 'id':instance_document.id})


class StationSiteForm(forms.ModelForm):
    """
    Add of a field to obtain the date of the creation and the associated project only when it'a new station
    else hide the field and the label
    """
    creation_date = forms.DateField(widget=widgets.AdminDateWidget,label='Date creation',required=False)
    project = forms.ModelChoiceField(queryset=Project.objects.all(),label='Projet',required=False)

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
            project_list = ProjectUser.objects.filter(user=self.current_user).values_list('project')
            self.fields['project'].queryset = Project.objects.filter(id__in=project_list)
            if len(project_list) == 1:
                self.fields['project'].empty_label=None

        # intialization
        operator_default_value = None
        try:
            operator_default_value = Actor.objects.get(actor_name='Inconnu')
        except (KeyError, Actor.DoesNotExist):
            pass

        self.fields['operator'].queryset = Actor.objects.filter(Q(actor_type=Actor.OBSERVATOIRE) | Q(actor_type=Actor.ORGANISME) | Q(actor_type=Actor.ENTREPRISE_SAV) | Q(actor_type=Actor.INCONNU))
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
        Check that the latitude, longitude and elevation are filled for a station, test and theoric site
        """
        if site_type in (StationSite.STATION, StationSite.SITE_TEST, StationSite.SITE_THEORIQUE) and (latitude == None or longitude == None or elevation == None):
            raise forms.ValidationError('Les champs latitude, longitude et elevation sont obligatoires pour ce type de site : %s' % dict(StationSite.SITE_CHOICES)[site_type])

        # Always return the full collection of cleaned data.
        return cleaned_data


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

        # Queryset to order by OSU and engineer to group them in
        # the drop down box.
        # Hack with the extra to sort by agency and after by actor_name
        # to bypass the agency actor_name.
        # TODO make custom widget for display a tree structure
        # by agency, contact.
        form.fields['actor'].queryset = Actor.objects.extra(select={"sortfield": "CASE WHEN id=actor_parent_id THEN actor_parent_id || '0' || actor_name ELSE actor_parent_id || '1' || actor_name END"}).order_by('sortfield')

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

    def __init__(self, *args, **kwargs):
        """
        Grabs the curried initial values and stores them into a 'private'
        variable. Note: the use of self.__initial is important, using
        self.initial or self._initial will be erased by a parent class
        """
        self.__initial = kwargs.pop('initial', [])
        super(IntervEquipInlineFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(IntervEquipInlineFormset, self).add_fields(form, index)

        url1 = reverse('xhr_equip_state')
        url2 = reverse('xhr_equipment')
        url3 = reverse('xhr_station')
        url4 = reverse('xhr_built')

        # TODO Ameliorer cette comparaison
        if self.__initial and self.__initial != ['']:
            equip = get_object_or_404(Equipment, id=self.__initial[0])
            form.fields['equip'].initial = equip

        STATE_CHOICES = []
        STATE_CHOICES.insert(0, ('', '-- choisir une action en premier --'))

        """
        Initialize form.fields
        """
        form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.none(), empty_label="-- choisir une action en premier --", widget=forms.Select(attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}))
        #form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.none(), empty_label="-- choisir une action en premier --")
        form.fields['equip_state'].widget = forms.Select(choices=STATE_CHOICES)
        form.fields['station'] = forms.ModelChoiceField(queryset = StationSite.objects.none(), widget=forms.Select(attrs={'onchange': 'get_site_built(this,\'' + url4 + '\');'}), empty_label="-- choisir une action en premier --")
        form.fields['built'] = forms.ModelChoiceField(queryset = Built.objects.none(), empty_label="-- choisir une action en premier --", required=False)

        """
        Hack to check if the formset is already filled to present the complete list of actions
        else the list exclude the action of buying (Acheter)
        """

        if index != None:
            """
            Obtain the value for each field of a line of a formset
            """
            action_id = form['equip_action'].value()
            equip_id = form['equip'].value()
            equip_state_id = form['equip_state'].value()
            station_id = form['station'].value()
            built_id = form['built'].value()

            try:
                intervention_station_id = instance.station.id
            except:
                intervention_station_id = station_id

            #intervention_station_id = self.instance.station.id
            #intervention_date = self.instance.intervention_date
            """
            06/08/2013 Add to keep the intervention number when we change the intervention date of an existing one
            This trick permit us to exclude the intervention from the function equip_state_todate and equip_place_todate_id
            We need this trick because the functions look in the DB for the state and place for a date before the change occur
            and if the date of the intervention change this interfere. Thus we have to exclude this from the query only if the date change
            """
            #intervention_id = self.instance.id

            """
            All actions can be display
            """
            if action_id != None and action_id != '' and int(action_id) == 1:
                ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
                ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))
            else:
                """
                The BUY action is not display
                """
                #ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS[1:]]
                """
                The BUY action is display
                """
                ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
                ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))


            ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))

            """
            Filtering the queryset depending of the value
            """
            if action_id != None and action_id != '':
                form.fields['equip_state'].widget = forms.Select(choices=available_equip_state(action_id))
                if intervention_station_id != None and intervention_station_id != '':
                    form.fields['station'] = forms.ModelChoiceField(queryset = available_station(action_id, intervention_station_id), widget=forms.Select(attrs={'onchange': 'get_site_built(this,\'' + url4 + '\');'}), empty_label=None)
                    if equip_id != None and equip_id != '':
                        form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.filter(pk=equip_id), widget=forms.Select(attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}), empty_label=None)
                    """
                    # The queryset of the equip field is not filtering because we trap the focus event on that field
                    if intervention_date != None and intervention_date != '':
                        # Permit the empty label because if the date of the intervention change the available_equipment can return to the queryset choices without the ancient value
                        form.fields['equip'] = forms.ModelChoiceField(queryset = available_equipment(action_id, intervention_station_id, intervention_date, intervention_id), widget=forms.Select(attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}))
                        #form.fields['equip'] = forms.ModelChoiceField(queryset = available_equipment(action_id, intervention_station_id, intervention_date, intervention_id))
                    """

            if station_id != None and station_id != '':
                form.fields['built'] = forms.ModelChoiceField(queryset = available_built(station_id), required=False)

        else :
            """
            The BUY action is not permit
            """
            #ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS[1:]]
            """
            The BUY action permitted
            """
            ACTION_CHOICES = [(c[0], c[1]) for c in EquipAction.EQUIP_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))

            """
            Special case if we came from a specific equipment
            """
            if self.__initial and self.__initial != ['']:
                equip = get_object_or_404(Equipment, id=self.__initial[0])
                form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.filter(id=self.__initial[0]), empty_label="-- choisir une action en premier --", initial=equip, widget=forms.Select(attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}))
                #form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.filter(id=self.__initial[0]), empty_label="-- choisir une action en premier --", initial=equip)
            else:
                form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.none(), empty_label="-- choisir une action en premier --", widget=forms.Select(attrs={'onfocus': 'get_equip(this,\'' + url2 + '\');'}))
                #form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.none(), empty_label="-- choisir une action en premier --")

        form.fields['equip_action'].widget = forms.Select(choices=ACTION_CHOICES, attrs={'onchange': 'get_equip_state(this,\'' + url1 + '\',\'' + url2 + '\',\'' + url3 + '\',\'' + url4 + '\');'})

    def clean(self):

        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
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
                intervention_station = StationSite.objects.get(id=intervention_station_id)
            except StationSite.DoesNotExist:
                intervention_station = StationSite.objects.none()
        else:
            intervention_station = StationSite.objects.none()

        date_intervention = self.data.get('intervention_date_0')
        heure_intervention = self.data.get('intervention_date_1')
        if date_intervention and heure_intervention:
            date_heure_intervention = u''.join([date_intervention,u' ',heure_intervention])
            try:
                naive_datetime = datetime.strptime(date_heure_intervention,"%Y-%m-%d %H:%M:%S")
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
                # Obtain the information from the formset needed for the validation
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
                    if equip_action == action and equip_place_todate_id(equip.id, intervention_date, int(intervention_id)) != int(intervention_station_id):
                        errors += 1

                if errors != 0:
                     raise forms.ValidationError('Equipement non present (%s) pour cette station (%s)' % (equip, intervention_station))


                """
                The action TESTER is valid only if the state were OPERATION, A_TESTER, DISPONIBLE, DEFAUT, PANNE or AUTRE before
                """
                if equip_action == EquipAction.TESTER and \
                   (equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.OPERATION and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.A_TESTER and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.DISPONIBLE and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.DEFAUT and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.PANNE and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.AUTRE):
                     raise forms.ValidationError('Equipement (%s) non dans un etat possible (%s) pour cette action (%s)' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date, int(intervention_id))-1][1], EquipAction.EQUIP_ACTIONS[equip_action-1][1]))

                """
                The action INSTALLER is valid only if the state was DISPONIBLE before
                """
                if equip_action == EquipAction.INSTALLER and \
                   equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.DISPONIBLE:
                     raise forms.ValidationError('Equipement (%s) non dans un etat disponible (%s) pour cette action (%s)' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date, int(intervention_id))-1][1], EquipAction.EQUIP_ACTIONS[equip_action-1][1]))

                """
                The action RECEVOIR is valid only if the state was EN_TRANSIT before
                """
                if equip_action == EquipAction.RECEVOIR and \
                   equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.EN_TRANSIT:
                     raise forms.ValidationError('Equipement (%s) n\'est pas actuellement en transit (%s) pour reception' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date, int(intervention_id))-1][1]))

                """
                The action RETROUVER is valid only if the state was DISPARU before
                """
                if equip_action == EquipAction.RETROUVER and \
                   equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.DISPARU:
                     raise forms.ValidationError('Equipement (%s) n\'est pas actuellement disparu (%s) pour etre retrouver' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date, int(intervention_id))-1][1]))

                """
                The action MAINT_CORR_DISTANTE or MAINT_CORR_SITE is valid only if the state was DEFAUT or PANNE before
                """
                if (equip_action == EquipAction.MAINT_CORR_DISTANTE or equip_action == EquipAction.MAINT_CORR_SITE) and \
                   (equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.DEFAUT and \
                    equip_state_todate(equip.id, intervention_date, int(intervention_id)) != EquipState.PANNE):
                     raise forms.ValidationError('Equipement (%s) n\'est pas actuellement en defaillance ou en panne (%s) pour maintenance corrective' % (equip, EquipState.EQUIP_STATES[equip_state_todate(equip.id, intervention_date, int(intervention_id))-1][1]))

                # TODO vue de validation
                # Validation of equip_action and target state
                errors = 0

                if equip_action == EquipAction.ACHETER and \
                   equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.TESTER and \
                   (equip_state != EquipState.OPERATION and \
                    equip_state != EquipState.A_TESTER and \
                    equip_state != EquipState.DISPONIBLE and \
                    equip_state != EquipState.DEFAUT and \
                    equip_state != EquipState.PANNE
                   ):
                    errors += 1
                if equip_action == EquipAction.INSTALLER and \
                   (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.DESINSTALLER and \
                   (equip_state != EquipState.A_TESTER and equip_state != EquipState.DISPONIBLE and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.CONSTATER_DEFAUT and \
                   (equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_PREV_DISTANTE and \
                   (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_CORR_DISTANTE and \
                   (equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_PREV_SITE and \
                   (equip_state != EquipState.DISPONIBLE and equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.MAINT_CORR_SITE and \
                   (equip_state != EquipState.DISPONIBLE and equip_state != EquipState.OPERATION and equip_state != EquipState.DEFAUT and equip_state != EquipState.PANNE):
                    errors += 1
                if equip_action == EquipAction.EXPEDIER and \
                   equip_state != EquipState.EN_TRANSIT:
                    errors += 1
                if equip_action == EquipAction.RECEVOIR and \
                   (equip_state != EquipState.A_TESTER and equip_state != EquipState.DISPONIBLE):
                    errors += 1
                if equip_action == EquipAction.METTRE_HORS_USAGE and \
                   equip_state != EquipState.HORS_USAGE:
                    errors += 1
                if equip_action == EquipAction.CONSTATER_DISPARITION and \
                   equip_state != EquipState.DISPARU:
                    errors += 1
                if equip_action == EquipAction.RETROUVER and \
                   equip_state != EquipState.A_TESTER:
                    errors += 1
                if equip_action == EquipAction.METTRE_AU_REBUT and \
                   equip_state != EquipState.AU_REBUT:
                    errors += 1

                if errors != 0:
                    raise forms.ValidationError('Etat final (%s) est invalide pour l\'action choisie  (%s)' % (EquipState.EQUIP_STATES[equip_state-1][1], EquipAction.EQUIP_ACTIONS[equip_action-1][1]))

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
                     raise forms.ValidationError('On doit effectuer cette action (%s) sur le site de l\'intervention (%s) et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], intervention_station, target_station))

                # The action DESINSTALLER is valid only if the target_station is an OSU
                if equip_action == EquipAction.DESINSTALLER and target_station.site_type != StationSite.OBSERVATOIRE:
                     raise forms.ValidationError('On doit effectuer cette action (%s) et entreposer dans un OSU et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                # The action EXPEDIER is valid only if the target_station is an OSU or SAV or AUTRE
                if equip_action == EquipAction.EXPEDIER and (target_station.site_type != StationSite.OBSERVATOIRE and target_station.site_type != StationSite.SAV and target_station.site_type != StationSite.AUTRE):
                     raise forms.ValidationError('On doit effectuer cette action (%s) et expedier vers OSU, SAV ou Autre et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                # The actions CONSTATER_DISPARITION and METTRE_AU_REBUT are valid only if the target_station is NEANT
                if (equip_action == EquipAction.CONSTATER_DISPARITION or equip_action == EquipAction.METTRE_AU_REBUT) and target_station.site_type != StationSite.NEANT:
                     raise forms.ValidationError('On doit effectuer cette action (%s) et indiquer un lieu indetermine (NEANT) et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                # The action ACHETER is valid only if the target_station is an OSU
                if equip_action == EquipAction.ACHETER and target_station.site_type != StationSite.OBSERVATOIRE:
                     raise forms.ValidationError('On doit effectuer cette action (%s) et indiquer un OSU et non (%s)' % (EquipAction.EQUIP_ACTIONS[equip_action-1][1], target_station))

                # The state DISPONIBLE is valid only if the target_station is an OSU
                if equip_state == EquipState.DISPONIBLE and (target_station.site_type != StationSite.OBSERVATOIRE and target_station.site_type != StationSite.STATION and target_station.site_type != StationSite.SITE_TEST) :
                     raise forms.ValidationError('Un equipement est (%s) seulement dans une station ou un OSU et non (%s)' % (EquipState.EQUIP_STATES[equip_state-1][1], target_station))

                # The state OPERATION is valid only if the target_station is an STATION_SISMOLOGIQUE
                if equip_state == EquipState.OPERATION and (target_station.site_type != StationSite.STATION and target_station.site_type != StationSite.SITE_TEST) :
                     raise forms.ValidationError('Un equipement est (%s) seulement dans une station et non dans un OSU (%s)' % (EquipState.EQUIP_STATES[equip_state-1][1], target_station))

        # Check that there is no more than one action per equip
        if not (len(set(Liste_equip)) == len(Liste_equip)):
            raise forms.ValidationError('On ne peut effectuer qu\'une seul action par equipement')


class IntervStationInlineFormset(forms.models.BaseInlineFormSet):
    def add_fields(self, form, index):
        super(IntervStationInlineFormset, self).add_fields(form, index)

        """
        Hack to check if the formset is already filled
        to present the complete list of actions
        else the list exclude the action of creating (Creer code station)
        """
        if index:
            ACTION_CHOICES = [(c[0], c[1]) for c in StationAction.STATION_ACTIONS]
            ACTION_CHOICES.insert(0, ('', '-- choisir une action --'))
        else:
            ACTION_CHOICES = [(c[0], c[1]) for c in StationAction.STATION_ACTIONS[1:]]
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
                if station_action == StationAction.CONSTATER_DEFAUT and (station_state != StationState.DEFAUT and station_state != StationState.PANNE):
                    errors += 1
                if station_action == StationAction.MAINT_PREV_DISTANTE and (station_state != StationState.DEFAUT and station_state != StationState.PANNE and station_state != StationState.OPERATION):
                    errors += 1
                if station_action == StationAction.MAINT_CORR_DISTANTE and (station_state != StationState.DEFAUT and station_state != StationState.PANNE and station_state != StationState.OPERATION):
                    errors += 1
                if station_action == StationAction.MAINT_PREV_SITE and (station_state != StationState.DEFAUT and station_state != StationState.PANNE and station_state != StationState.OPERATION):
                    errors += 1
                if station_action == StationAction.MAINT_CORR_SITE and (station_state != StationState.DEFAUT and station_state != StationState.PANNE and station_state != StationState.OPERATION):
                    errors += 1
                if station_action == StationAction.DEMANTELER and station_state != StationState.FERMEE:
                    errors += 1

                if errors != 0:
                    raise forms.ValidationError('Etat (%s) invalide pour l\'action choisi  (%s)' % (StationState.STATION_STATES[station_state-1][1], StationAction.STATION_ACTIONS[station_action-1][1]))


"""
class ChainConfigInlineFormset(forms.models.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.__initial = kwargs.pop('initial', [])
        super(ChainConfigInlineFormset, self).__init__(*args, **kwargs)
"""
class ChainInlineFormset(forms.models.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):

#        Grabs the curried initial values and stores them into a 'private'
#        variable. Note: the use of self.__initial is important, using
#        self.initial or self._initial will be erased by a parent class
        self.__initial = kwargs.pop('initial', [])
        super(ChainInlineFormset, self).__init__(*args, **kwargs)

    def add_fields(self, form, index):
        super(ChainInlineFormset, self).add_fields(form, index)

        # TODO Ameliorer cette comparaison
        if self.__initial and self.__initial != ['']:
            station = get_object_or_404(StationSite, id=self.__initial[0])
            form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.all())

        url = reverse('xhr_equip_oper')

        """
        Initialize form.fields
        """
        ORDER_CHOICES = [(c[0], c[1]) for c in Chain.ORDER_CHOICES]
        ORDER_CHOICES.insert(0, ('', '-- choisir un type en premier --'))

        #ORDER_CHOICES = [('', '-- choisir un ordre en premier --'),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),]
        form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.none(), empty_label="-- choisir un type en premier --")
        form.fields['order'].widget = forms.Select(choices=ORDER_CHOICES, attrs={'onchange': 'get_equip_oper(this,\'' + url + '\');'})

        if index != None :
            #
            # Ne sera plus necessaire apres l'utilisation de la fonction
            # available_equipment_scioper
            #
            #equip_id = form['equip'].value()
            #if equip_id != '':
            #    form.fields['equip'] = forms.ModelChoiceField(queryset = Equipment.objects.filter(pk=equip_id), empty_label=None)

            try:
                channel_station_id = self.instance.station.id
                channel_date = self.instance.start_date
                form.fields['equip'] = forms.ModelChoiceField(queryset = available_equipment_scioper(channel_station_id, channel_date), empty_label=None)
            except:
                return


class ChannelForm(forms.ModelForm):
    """
    Obtain the latitude, longitude and elevation of the station
    the first time we add channel via the site form
    """
#    distance_x = forms.DecimalField(required=False)
#    distance_y = forms.DecimalField(required=False)
#    distance_z = forms.DecimalField(required=False)

    class Meta:
        model = Channel
        fields = "__all__"

    # Hack field to show only if channel code and sample rate not fit
    accept_anyway = forms.BooleanField(initial=False,required=False)

    def __init__(self, *args, **kwargs):
        super(ChannelForm, self).__init__(*args, **kwargs)

        # Hack to simulate warning message via raise Validationerror
        if "accept_anyway" in self.errors:
            self.fields['accept_anyway'].widget = forms.CheckboxInput()
        else:
            self.fields['accept_anyway'].widget = forms.HiddenInput()
            self.fields['accept_anyway'].label = ""

#        instance = getattr(self, 'instance', None)
#        if instance and instance.pk:
#            station = get_object_or_404(StationSite, id=instance.station.id)
#            self.fields['distance_x'].initial = (float(instance.longitude) - float(station.longitude)) * (111.111 * math.cos(float(instance.latitude) * math.pi / 180))
#            self.fields['distance_y'].initial = (float(instance.latitude) - float(station.latitude)) * 111.111
#            self.fields['distance_z'].initial = float(instance.elevation) - float(station.elevation)
#            self.fields['distance_x'].widget.attrs['readonly'] = True
#            self.fields['distance_y'].widget.attrs['readonly'] = True
#            self.fields['distance_z'].widget.attrs['readonly'] = True

#        station_label = ""
        if 'initial' in kwargs:
            initial = kwargs['initial']
            if 'station' in initial:
                station = get_object_or_404(StationSite, id=initial['station'])
                self.fields['latitude'].initial = station.latitude
                self.fields['longitude'].initial = station.longitude
                self.fields['elevation'].initial = station.elevation
                self.fields['station'].initial = station.id

        url = reverse('xhr_station_position')

        self.fields['depth'].initial = '0'
        split_widget = widgets.AdminSplitDateTime()
        split_widget.widgets[0].attrs = {'class': 'vDateField', 'size': '10'}
        split_widget.widgets[1].attrs = {'class': 'vTimeField', 'size': '8', 'value': '00:00:00'}
        self.fields['start_date'].widget = split_widget
        self.fields['location_code'].initial = '00'
        self.fields['location_code'].required = False

        """
        CHANNEL_CHOICES = [('', '---'),('BHE','BHE'),('BHN','BHN'),('BHZ','BHZ'), \
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
        #self.fields['channel_code'].widget = forms.Select(choices=CHANNEL_CHOICES, attrs={'onchange':'get_dip_azimut_value(this);'})
        self.fields['channel_code'] = forms.ModelChoiceField(queryset = ChannelCode.objects.all().order_by('presentation_rank'), widget=forms.Select(attrs={'onchange':'get_dip_azimut_value(this);'}), empty_label='--')
        self.fields['station'] = forms.ModelChoiceField(queryset = StationSite.objects.all())
        self.fields["data_type"].widget = CheckboxSelectMultiple()
        self.fields["data_type"].queryset = DataType.objects.all()
        self.fields["data_type"].initial = [t.pk for t in DataType.objects.filter(Q(type_description='CONTINUOUS')| Q(type_description='GEOPHYSICAL'))]

    def clean(self):

        cleaned_data = super(ChannelForm, self).clean()
        channel_code = cleaned_data.get("channel_code")
        sample_rate = cleaned_data.get("sample_rate")
        accept = cleaned_data.get("accept_anyway")

        # Check that the sample rate fit in the range for the channel code
        # We can bypass this validation with the accept field
        # http://www.iris.edu/manuals/SEED_appA.htm
        if channel_code:
            if channel_code.channel_code and not(sample_rate == None):
                if not accept and \
                    ((channel_code.channel_code[0] == 'D' and not(sample_rate >= 250 and sample_rate < 1000)) or \
                     (channel_code.channel_code[0] == 'C' and not(sample_rate >= 250 and sample_rate < 1000)) or \
                     (channel_code.channel_code[0] == 'E' and not(sample_rate >= 80 and sample_rate < 250)) or \
                     (channel_code.channel_code[0] == 'S' and not(sample_rate >= 10 and sample_rate < 80)) or \
                     (channel_code.channel_code[0] == 'H' and not sample_rate >= 80) or \
                     (channel_code.channel_code[0] == 'B' and not(sample_rate >= 10 and sample_rate < 80)) or \
                     (channel_code.channel_code[0] == 'M' and not(sample_rate > 1 and sample_rate < 10)) or \
                     (channel_code.channel_code[0] == 'L' and not(sample_rate == 1)) or \
                     (channel_code.channel_code[0] == 'V' and not(sample_rate == 0.1)) or \
                     (channel_code.channel_code[0] == 'U' and not(sample_rate == 0.01))):
                    self.add_error('sample_rate', _("Sample rate unexpected."))
                    self.add_error('accept_anyway', _("Bypass error."))
                    raise forms.ValidationError('Sample rate (%s) not in the range for this channel code (%s)' % (sample_rate, channel_code.channel_code))
        # Always return the full collection of cleaned data.
        return cleaned_data


class ProjectUserForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProjectUserForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            self.fields['user'] = forms.ModelChoiceField(queryset=User.objects.filter(pk=self.instance.user.id), empty_label=None)


class ChainConfigInlineFormset(forms.models.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(ChainConfigInlineFormset, self).add_fields(form, index)

        url1 = reverse('xhr_parameter_value')

        #form.fields['parameter'] = forms.ModelChoiceField(queryset = ParameterEquip.objects.filter(equip_model_id=self.instance.equip.equip_model.id), widget=forms.Select(attrs={'onchange': "alert('test');"}))
        form.fields['parameter'] = forms.ModelChoiceField(queryset = ParameterEquip.objects.filter(equip_model_id=self.instance.equip.equip_model.id), widget=forms.Select(attrs={'onchange': 'get_parameter_value(this,\'' + url1 + '\');'}))
        form.fields['value'] = forms.ModelChoiceField(queryset = ParameterValue.objects.all(), widget=forms.Select(attrs={'onfocus': 'get_parameter_value(this,\'' + url1 + '\');'}), empty_label="-- choisir un parametre en premier --")


class ChannelChainInlineFormset(forms.models.BaseInlineFormSet):

    def add_fields(self, form, index):
        super(ChannelChainInlineFormset, self).add_fields(form, index)

        if index != None:
            """
            Obtain the value for each field of a line of a formset
            """
            parameter_id = form['parameter'].value()

            form.fields['parameter'] = forms.ModelChoiceField(queryset = ParameterEquip.objects.filter(pk=parameter_id), empty_label=None)
            form.fields['value'] = forms.ModelChoiceField(queryset = ParameterValue.objects.filter(parameter_id=parameter_id), empty_label=None)
