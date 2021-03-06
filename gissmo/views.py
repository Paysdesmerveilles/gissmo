# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os.path
import mimetypes
from datetime import datetime

# delete simplejson from django.utils as Django 1.7 deliver it not
import json

from django.db.models import (
    Q,
    get_model)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
    HttpResponseRedirect,
    HttpResponse)
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.utils.encoding import smart_text


from equipment import states as EquipState
from equipment import actions as EquipAction
from equipment.models import ChangeModelModification

from station import states as StationState
from station import actions as StationAction

from gissmo.models import *  # NOQA
from gissmo.tools import DecimalEncoder, timezone_aware

from django.contrib.admin import site


def site_maps(request):
    query = request.GET.get('Station', '')
    ResHistStations = []
    ResStationUnique = []
    StationUnique = ''
    Liste = []

    Stations = StationSite.objects.filter(site_type=1)

    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(StationSite)
    application_label = content_type.app_label

    for station in Stations:
        last_station_state = IntervStation.objects.filter(
            intervention__station=station,
            station_state__isnull=False).order_by(
                '-intervention__intervention_date')[:1]
        if last_station_state:
            for last in last_station_state:
                Liste.append(last.id)

    ResStatTest = StationSite.objects.filter(site_type=6)
    ResStatTheo = StationSite.objects.filter(site_type=7)
    ResHistStations = IntervStation.objects.filter(id__in=Liste)

    if query:
        ResStationUnique = IntervStation.objects.filter(
            intervention__station=query,
            station_state__isnull=False).order_by(
                '-intervention__intervention_date')[:1]
        if ResStationUnique:
            for resstationunique in ResStationUnique:
                StationUnique = resstationunique.intervention.station

    return render(request, "site_gmap.html", {
        "ResHistStations": ResHistStations,
        "query": query,
        "StationUnique": StationUnique,
        "ResStatTheo": ResStatTheo,
        "ResStatTest": ResStatTest,
        "application_label": application_label,
        "site_header": site.site_header,
    })

site_maps = staff_member_required(site_maps)


def itineraire_maps(request):
    query = request.GET.get('Station', '')
    ResStationUnique = ''
    Observatoire = ''

    if query:
        ResStationUnique = StationSite.objects.get(pk=query)

    # Un utilisateur ne doit avoir que deux groupes resif et l'observatoire
    # d'attache
    user_group_list = request.user.groups.exclude(
        name__iexact="Resif").values_list('name', flat=True)

    #   Verification si la liste est vide
    # Le point de depart est l'EOST, si le user n'a pas d'observatoire assigne
    # ou si l'observatoire n'est pas inscrit comme une station
    if user_group_list:
        user_group = user_group_list[0]
    else:
        user_group = 'EOST'

    try:
        Observatoire = StationSite.objects.get(station_code=user_group)
    except StationSite.DoesNotExist:
        Observatoire = StationSite.objects.get(station_code='EOST')

    return render(request, "itineraire_gmap.html", {
        "ResStationUnique": ResStationUnique,
        "Observatoire": Observatoire,
    })

itineraire_maps = staff_member_required(itineraire_maps)


def get_file(request, app_label, model_name, field_name, identifier):
    """
    Function that check if the user can open the file and do so.
    The request user must not be anonymous, authenticated and be the owner
    of the file or be in the same group of the owner.
    """
    mimetypes.init()
    default_type = 'application/octet-stream'

    # Obtain the model on which we work : StationDoc, EquipDoc or EquipModelDoc
    model = get_model(app_label, model_name)

    # Obtain the instance
    instance = get_object_or_404(model, pk=identifier)

    if (not request.user.is_anonymous()) and request.user.is_authenticated():
        # and ((instance.owner.pk == request.user.pk) or
        # (set(instance.owner.groups.all()) ==
        # set(request.user.groups.all()))):
        path = getattr(instance, field_name).file.name
        file_name = os.path.basename(path)
        mime_type_guess = mimetypes.guess_type(file_name)
        fsock = open(path, "rb")
        if mime_type_guess is not None and mime_type_guess[0] is not None:
            response = HttpResponse(fsock, content_type=mime_type_guess[0])
        elif mime_type_guess[0] is None:
            response = HttpResponse(fsock, content_type=default_type)
        response['Content-Disposition'] = 'attachment; filename=' + \
            smart_text(file_name)
        return response
    else:
        raise PermissionDenied()

# TODO: fonction qui selon station_action choisi retourne station_state
# possible


def xhr_station_state(request):
    """
    Request that return the possible status for a station according to the
    action done.
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':

        def get_choices(states=[]):
            res = []
            for state in states:
                display = dict(StationState.STATION_STATES)[state]
                choice = {
                    'optionValue': state,
                    'optionDisplay': str(display)}
                res.append(choice)
            return res

        action = request.GET.get('action', '')
        if not isinstance(action, int):
            action = int(action)
        select_choice = [({"optionValue": c[0], "optionDisplay": str(c[1])})
                         for c in StationState.STATION_STATES]
        select_choice.insert(
            0, ({
                "optionValue": '',
                "optionDisplay": '-- first select an action --'}))
        is_creer = action == StationAction.CREER
        is_installer = action == StationAction.INSTALLER
        prev_and_corr_actions = [
            StationAction.MAINT_PREV_DISTANTE,
            StationAction.MAINT_CORR_DISTANTE,
            StationAction.MAINT_PREV_SITE,
            StationAction.MAINT_CORR_SITE]
        if is_creer or is_installer:
            select_choice = get_choices([StationState.INSTALLATION])
        elif action == StationAction.DEBUTER_TEST:
            select_choice = get_choices([
                StationState.EN_TEST,
                StationState.OPERATION])
        elif action == StationAction.TERMINER_TEST:
            select_choice = get_choices([
                StationState.FERMEE,
                StationState.OPERATION])
        elif action == StationAction.OPERER:
            select_choice = get_choices([StationState.OPERATION])
        elif action == StationAction.CONSTATER_DEFAUT:
            select_choice = get_choices([
                StationState.DEFAUT,
                StationState.PANNE])
        elif action in prev_and_corr_actions:
            select_choice = get_choices([
                StationState.OPERATION,
                StationState.DEFAUT,
                StationState.PANNE])
        elif action == StationAction.DEMANTELER:
            select_choice = get_choices([StationState.FERMEE])
        elif action == StationAction.AUTRE:
            pass
        else:
            pass
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def available_equip_state(action):
    """
    Function that return a list of status according to the action via the
    parameter.
    This is use on add_fields section of the IntervEquipInlineFormset and in
    xhr_equip_state function.
    """
    # Prepare some values
    select_choice = [(c[0], c[1]) for c in EquipState.EQUIP_STATES]
    select_choice.insert(0, ('', '-- first select an action --'))
    if not isinstance(action, int):
        action = int(action)
    is_prev_dist = action == EquipAction.MAINT_PREV_DISTANTE
    is_corr_dist = action == EquipAction.MAINT_CORR_DISTANTE
    is_prev_site = action == EquipAction.MAINT_PREV_SITE
    is_corr_site = action == EquipAction.MAINT_CORR_SITE
    if action == EquipAction.ACHETER:
        select_choice = [(EquipState.A_TESTER, EquipState.EQUIP_STATES[
                          EquipState.A_TESTER - 1][1])]
    elif action == EquipAction.TESTER:
        select_choice = [(EquipState.DISPONIBLE, EquipState.EQUIP_STATES[
                          EquipState.DISPONIBLE - 1][1])]
        select_choice.append((EquipState.OPERATION, EquipState.EQUIP_STATES[
                             EquipState.OPERATION - 1][1]))
        select_choice.append((EquipState.A_TESTER, EquipState.EQUIP_STATES[
                             EquipState.A_TESTER - 1][1]))
        select_choice.append(
            (EquipState.DEFAUT,
                EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1]))
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif action == EquipAction.INSTALLER:
        select_choice = [(
            EquipState.OPERATION,
            EquipState.EQUIP_STATES[EquipState.OPERATION - 1][1])]
        select_choice.append(
            (EquipState.DEFAUT,
                EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1]))
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif action == EquipAction.DESINSTALLER:
        select_choice = [(
            EquipState.A_TESTER,
            EquipState.EQUIP_STATES[EquipState.A_TESTER - 1][1])]
        select_choice.append((
            EquipState.DISPONIBLE,
            EquipState.EQUIP_STATES[EquipState.DISPONIBLE - 1][1]))
        select_choice.append(
            (EquipState.DEFAUT,
                EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1]))
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif action == EquipAction.CONSTATER_DEFAUT:
        select_choice = [(
            EquipState.DEFAUT,
            EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1])]
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif is_prev_dist or is_corr_dist:
        select_choice = [(
            EquipState.OPERATION,
            EquipState.EQUIP_STATES[EquipState.OPERATION - 1][1])]
        select_choice.append(
            (EquipState.DEFAUT,
                EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1]))
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif is_prev_site or is_corr_site:
        select_choice = [(
            EquipState.DISPONIBLE,
            EquipState.EQUIP_STATES[EquipState.DISPONIBLE - 1][1])]
        select_choice.append((
            EquipState.OPERATION,
            EquipState.EQUIP_STATES[EquipState.OPERATION - 1][1]))
        select_choice.append(
            (EquipState.DEFAUT,
                EquipState.EQUIP_STATES[EquipState.DEFAUT - 1][1]))
        select_choice.append(
            (EquipState.PANNE,
                EquipState.EQUIP_STATES[EquipState.PANNE - 1][1]))
    elif action == EquipAction.EXPEDIER:
        select_choice = [(
            EquipState.EN_TRANSIT,
            EquipState.EQUIP_STATES[EquipState.EN_TRANSIT - 1][1])]
    elif action == EquipAction.RECEVOIR:
        select_choice = [(
            EquipState.A_TESTER,
            EquipState.EQUIP_STATES[EquipState.A_TESTER - 1][1])]
        select_choice.append((
            EquipState.DISPONIBLE,
            EquipState.EQUIP_STATES[EquipState.DISPONIBLE - 1][1]))
    elif action == EquipAction.METTRE_HORS_USAGE:
        select_choice = [(
            EquipState.HORS_USAGE,
            EquipState.EQUIP_STATES[EquipState.HORS_USAGE - 1][1])]
    elif action == EquipAction.CONSTATER_DISPARITION:
        select_choice = [(
            EquipState.DISPARU,
            EquipState.EQUIP_STATES[EquipState.DISPARU - 1][1])]
    elif action == EquipAction.RETROUVER:
        select_choice = [(
            EquipState.A_TESTER,
            EquipState.EQUIP_STATES[EquipState.A_TESTER - 1][1])]
    elif action == EquipAction.METTRE_AU_REBUT:
        select_choice = [(
            EquipState.AU_REBUT,
            EquipState.EQUIP_STATES[EquipState.AU_REBUT - 1][1])]
    elif action == EquipAction.AUTRE:
        pass
    else:
        pass
    return select_choice


def xhr_equip_state(request):
    """
    Request that return the possible statuses for a station according to the
    action done.
    This use onchange event.
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action = request.GET.get('action', '')

        select_choice = [({"optionValue": c[0], "optionDisplay": str(c[1])})
                         for c in available_equip_state(action)]
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def equip_state_todate(equip, date, intervention_id):
    """
    Function to obtain the equipment status at a precise moment
    """
    result = 0
    if intervention_id:
        """
        Check that the date of the intervention has not changed
        If yes, we must exclude the intervention form the search
        """
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        if date != intervention.intervention_date:
            last_equip_state = IntervEquip.objects.exclude(
                intervention__pk=intervention_id).filter(
                    intervention__intervention_date__lt=date,
                    equip__id=equip,
                    equip_state__isnull=False).order_by(
                        '-intervention__intervention_date')[:1]
        else:
            last_equip_state = IntervEquip.objects.filter(
                intervention__intervention_date__lt=date,
                equip__id=equip,
                equip_state__isnull=False).order_by(
                    '-intervention__intervention_date')[:1]
    else:
        last_equip_state = IntervEquip.objects.filter(
            intervention__intervention_date__lt=date,
            equip__id=equip,
            equip_state__isnull=False).order_by(
                '-intervention__intervention_date')[:1]

    if last_equip_state:
        for last in last_equip_state:
            result = last.equip_state
    return result


def equip_with_state_todate(date, intervention_id):
    """
    Function to obtain equipment status at a precise moment
    """
    liste = []
    equipments = Equipment.objects.all()
    for equip in equipments:
        if intervention_id:
            """
            Check that the date of the intervention has not changed
            If yes, we must exclude the intervention form the search
            """
            intervention = get_object_or_404(Intervention, pk=intervention_id)
            if date != intervention.intervention_date:
                last_equip_state = IntervEquip.objects.exclude(
                    intervention__pk=intervention_id).filter(
                        intervention__intervention_date__lt=date,
                        equip__id=equip.id,
                        equip_state__isnull=False).order_by(
                            '-intervention__intervention_date')[:1]
            else:
                last_equip_state = IntervEquip.objects.filter(
                    intervention__intervention_date__lt=date,
                    equip__id=equip.id,
                    equip_state__isnull=False).order_by(
                        '-intervention__intervention_date')[:1]
        else:
            last_equip_state = IntervEquip.objects.filter(
                intervention__intervention_date__lt=date,
                equip__id=equip.id,
                equip_state__isnull=False).order_by(
                    '-intervention__intervention_date')[:1]

        if last_equip_state:
            if last_equip_state[0].equip_state == 3:
                liste.append(equip)
    return liste

#
# TODO eliminate one of this function
#
# equip_place_todate return the station object
# equip_place_todate_id return the station id
#


def equip_place_todate(equip, date):
    """
    Function to obtain the place of an equipment at a precise moment
    """
    result = 0
    last_equip_place = IntervEquip.objects.filter(
        intervention__intervention_date__lt=date,
        equip__id=equip,
        station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_place:
        for last in last_equip_place:
            result = last.station
    return result


def equip_place_todate_id(equip, date, intervention_id):
    """
    Function to obtain the place of an equipment at a precise moment
    This function return the id of the site
    """
    result = 0
    if intervention_id:
        """
        Check that the date of the intervention has not changed
        If yes, we must exclude the intervention form the search
        """
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        if date != intervention.intervention_date:
            last_equip_place = IntervEquip.objects.exclude(
                intervention__pk=intervention_id).filter(
                    intervention__intervention_date__lte=date,
                    equip__id=equip,
                    station__isnull=False).order_by(
                        '-intervention__intervention_date')[:1]
        else:
            last_equip_place = IntervEquip.objects.filter(
                intervention__intervention_date__lte=date,
                equip__id=equip,
                station__isnull=False).order_by(
                    '-intervention__intervention_date')[:1]
    else:
        last_equip_place = IntervEquip.objects.filter(
            intervention__intervention_date__lte=date,
            equip__id=equip,
            station__isnull=False).order_by(
                '-intervention__intervention_date')[:1]

    if last_equip_place:
        for last in last_equip_place:
            result = last.station_id
    return result


def available_equipment_cursor(action, station, date, intervention_id):

    # Check if intervention_id is set to something else put the value 0
    if not intervention_id:
        intervention_id = 0
    else:
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        # Trick : If the date and site have not changed we put 0 as
        # intervention.
        # There is no intervention with the ID 0 but we can keep the same code
        is_same_date = date == intervention.intervention_date
        if is_same_date and int(station) == intervention.station_id:
            intervention_id = 0

    equipment_list = []

    # Use 'with connection.cursor()' instead of c = connection.cursor() as
    # explained in https://docs.djangoproject.com/en/1.8/releases/1.7/
    # using-database-cursors-as-context-managers
    with connection.cursor() as cursor:
        """
        Give the last status and station of an equipment
        If the intervention date or time change via the form of the
        intervention we exclude this intervention to permit the change of those
        fields (date and time).
        """
        sql = """
        SELECT equip_id, intervention_date, station_id, equip_state
        FROM (
            SELECT DISTINCT ON (interv.equip_id)
                interv.equip_id,
                interv.intervention_date,
                interv.station_id,
                interv.equip_state
            FROM (
                SELECT
                    gissmo_intervequip.equip_id,
                    gissmo_intervention.intervention_date,
                    gissmo_intervequip.station_id,
                    gissmo_intervequip.equip_state
                FROM
                    public.gissmo_intervequip,
                    public.gissmo_intervention
                WHERE
                    gissmo_intervention.id != %s and
                    gissmo_intervention.intervention_date < %s and
                    gissmo_intervequip.intervention_id = gissmo_intervention.id
            ) AS interv
            ORDER BY interv.equip_id, interv.intervention_date DESC
        ) AS it
        """
        cursor.execute(sql, [intervention_id, date])

        # Buy only equip that were never buy in the system
        if not isinstance(action, int):
            action = int(action)
        corrective_maintenance_states = [
            EquipAction.MAINT_CORR_DISTANTE,
            EquipAction.MAINT_CORR_SITE]
        if action == EquipAction.ACHETER:
            # Obtain all intervention with BUY as action
            equip_purchased = IntervEquip.objects.exclude(
                intervention__pk=intervention_id).filter(
                    equip_action=EquipAction.ACHETER)
            list_equip_purchased = []
            for equip in equip_purchased:
                list_equip_purchased.append(equip.equip.id)

            # Obtain all equip without BUY action
            nobuy_equipments = Equipment.objects.exclude(
                id__in=list_equip_purchased)
            for equip in nobuy_equipments:
                equipment_list.append(equip.id)
        # Install only equip DISPONIBLE or No status
        elif action == EquipAction.INSTALLER:
            for row in cursor.fetchall():
                if row[3] == EquipState.DISPONIBLE:
                    equipment_list.append(row[0])
        # Receive only equip En transit or No status
        elif action == EquipAction.RECEVOIR:
            for row in cursor.fetchall():
                if row[3] == EquipState.EN_TRANSIT:
                    equipment_list.append(row[0])
        # Retreive only equip Disparu
        elif action == EquipAction.RETROUVER:
            for row in cursor.fetchall():
                if row[3] == EquipState.DISPARU:
                    equipment_list.append(row[0])
        # Corrective maintenance only equip installed in the station in the
        # following status DEFAUT ou PANNE
        elif action in corrective_maintenance_states:
            for row in cursor.fetchall():
                allowed_states = [
                    EquipState.DEFAUT,
                    EquipState.PANNE]
                if row[2] == int(station) and row[3] in allowed_states:
                    equipment_list.append(row[0])
        # Make action only on equip installed in the station
        else:
            for row in cursor.fetchall():
                if row[2] == int(station):
                    equipment_list.append(row[0])

    equip_dispo = Equipment.objects.filter(id__in=equipment_list).order_by(
        'equip_model__equip_type__equip_supertype',
        'equip_model__equip_type',
        'equip_model',
        'serial_number')
    return equip_dispo

"""
The function available_equipment will be remplaced by
available_equipment_cursor for a better response time.
"""


def available_equipment(action, station, date, intervention_id):

    # Check if intervention_id is set to something else put the value 0
    if not intervention_id:
        intervention_id = 0

    equipment_list = []
    equipments = Equipment.objects.all()
    if not isinstance(action, int):
        action = int(action)
    corrective_maintenance_actions = [
        EquipAction.MAINT_CORR_DISTANTE,
        EquipAction.MAINT_CORR_SITE]
    # Buy only equip with No status
    if action == EquipAction.ACHETER:
        # Obtain all intervention with BUY as action
        equip_purchased = IntervEquip.objects.exclude(
            intervention__pk=intervention_id).filter(
                equip_action=EquipAction.ACHETER)
        list_equip_purchased = []
        for equip in equip_purchased:
            list_equip_purchased.append(equip.equip.id)

        # Obtain all equip without BUY action
        nobuy_equipments = Equipment.objects.exclude(
            id__in=list_equip_purchased)
        for equip in nobuy_equipments:
            equipment_list.append(equip.id)
    # Install only equip DISPONIBLE or No status
    elif action == EquipAction.INSTALLER:
        for equip in equipments:
            todate_state = equip_state_todate(
                equip.id,
                date,
                int(intervention_id))
            if todate_state == EquipState.DISPONIBLE:
                equipment_list.append(equip.id)
    # Receive only equip En transit or No status
    elif action == EquipAction.RECEVOIR:
        for equip in equipments:
            todate_state = equip_state_todate(
                equip.id,
                date,
                int(intervention_id))
            if todate_state == EquipState.EN_TRANSIT:
                equipment_list.append(equip.id)
    # Retreive only equip Disparu
    elif action == EquipAction.RETROUVER:
        for equip in equipments:
            todate_state = equip_state_todate(
                equip.id,
                date,
                int(intervention_id))
            if todate_state == EquipState.DISPARU:
                equipment_list.append(equip.id)
    # Corrective maintenance only equip installed in the station in the
    # following status DEFAUT ou PANNE
    elif action in corrective_maintenance_actions:
        allowed_states = [
            EquipState.DEFAUT,
            EquipState.PANNE]
        for equip in equipments:
            todate_id = int(equip_place_todate_id(
                equip.id,
                date,
                int(intervention_id)))
            if todate_id == int(station):
                equip_state = equip_state_todate(
                    equip.id,
                    date,
                    int(intervention_id))
                if equip_state in allowed_states:
                    equipment_list.append(equip.id)
    # Make action only on equip installed in the station
    else:
        for equip in equipments:
            todate_id = int(equip_place_todate_id(
                equip.id,
                date,
                int(intervention_id)))
            if todate_id == int(station):
                equipment_list.append(equip.id)

    equip_dispo = Equipment.objects.filter(
        id__in=equipment_list).order_by(
            'equip_model__equip_type__equip_supertype',
            'equip_model__equip_type',
            'equip_model',
            'serial_number')
    return equip_dispo


def xhr_equipment(request):
    """
    Request that return the possible equipment for a station according to the
    action done.
    equipment available
    equipment on site
    """

    if request.is_ajax() and request.method == 'GET':
        action = request.GET.get('action', '')
        station = request.GET.get('station', '')
        date_intervention = request.GET.get('date', '')
        heure_intervention = request.GET.get('heure', '')
        intervention_id = request.GET.get('intervention', '')

        # From :
        # https://docs.djangoproject.com/en/dev/topics/i18n/timezones/#troubleshooting
        date_heure_intervention = u''.join(
            [date_intervention, u' ', heure_intervention])
        naive_datetime = datetime.strptime(
            date_heure_intervention, "%Y-%m-%d %H:%M:%S")
        date_intervention = timezone_aware(naive_datetime)

        equip_dispo = available_equipment_cursor(
            action, station, date_intervention, intervention_id)

        select_choice = [{
            "optionValue": "",
            "optionDisplay": "-- Select an equipment --"}]
        for equip in equip_dispo:
            select_choice.append(({
                "optionValue": equip.id,
                "optionDisplay": str(equip)}))
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

# TODO fonction qui selon equip_action choisi retourne emplacement
# possible stations, bati, equipement hote


def available_station(action, station):
    """
    Function that return a queryset of station according to the action and
    station on which the intervention occur.
    This is use on add_fields section of the IntervEquipInlineFormset and in
    xhr_station function.
    """
    if not isinstance(action, int):
        action = int(action)
    # Send equipment somewhere SAV, OSU or Other
    if action == EquipAction.EXPEDIER:
        station_dispo = StationSite.objects.filter(
            Q(site_type=StationSite.OBSERVATOIRE) |
            Q(site_type=StationSite.SAV) |
            Q(site_type=StationSite.AUTRE)).order_by('station_code')
    # Uninstall and put the equip in OSU or in the station of the intervention
    elif action == EquipAction.DESINSTALLER:
        station_dispo = StationSite.objects.filter(
            site_type=StationSite.OBSERVATOIRE).order_by('station_code')
    # Not able to know where is the equipment
    elif action == EquipAction.CONSTATER_DISPARITION:
        station_dispo = StationSite.objects.filter(
            site_type=StationSite.NEANT).order_by('station_code')
    # Stop tracking the equipment
    elif action == EquipAction.METTRE_AU_REBUT:
        station_dispo = StationSite.objects.filter(
            site_type=StationSite.NEANT).order_by('station_code')
    # Out of service but can stay in the station or place to a observatory or
    # nowhere
    elif action == EquipAction.METTRE_HORS_USAGE:
        station_dispo = StationSite.objects.filter(
            Q(id=station) |
            Q(site_type=StationSite.OBSERVATOIRE) |
            Q(site_type=StationSite.NEANT)).order_by('station_code')
    # Make action only on equip installed in the station
    else:
        station_dispo = StationSite.objects.filter(id=station)

    return station_dispo


def xhr_station(request):
    """
    Request that return the possible station according to the action done
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action = request.GET.get('action', '')
        station = request.GET.get('station', '')

        # If action return only one site this is the only choice possible else
        # we have to select a site
        station_dispo = available_station(action, station)
        if station_dispo.count() == 1:
            select_choice = []
        else:
            select_choice = [{
                "optionValue": "",
                "optionDisplay": "-- Select a site --"}]
        for station in station_dispo:
            select_choice.append(({
                "optionValue": station.id,
                "optionDisplay": str(station)}))
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def available_built(station):
    """
    Function that return a queryset of building according to the station on
    which the action occur.
    This is use on add_fields section of the IntervEquipInlineFormset and in
    xhr_built function.
    """
    built_dispo = Built.objects.filter(station__id=station)

    return built_dispo


def xhr_built(request):
    """
    Request that return the possible built according to the station
    """
    if request.is_ajax() and request.method == 'GET':
        station = request.GET.get('station', '')

        built_dispo = available_built(station)

        select_choice = [{
            "optionValue": "",
            "optionDisplay": "-- Select a place --",
        }]
        for built in built_dispo:
            select_choice.append(({
                "optionValue": built.id,
                "optionDisplay": str(built)}))
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def available_equipment_scioper(station_id, date):
    """
    Function that return a queryset of scientific equipment in place at the
    station for the date specify.
    This is use on add_fields section of the ChainInlineFormset and in
    xhr_equip_oper function.
    """
    equipment_list = []
    if not isinstance(station_id, int):
        station_id = int(station_id)
    # WARNING: If the supertype name change we have to change the code too
    # TODO: Find another way to filter equipments, like a checkbox on
    # equipment's supertype: "For acquisition chain" (for an example)
    a = "01. Scientifique"
    b = "06. Ordinateur"

    allowed = EquipSupertype.objects.filter(
        Q(equip_supertype_name=a) | Q(equip_supertype_name=b))
    interventions = IntervEquip.objects.filter(
        intervention__intervention_date__lte=date,
        station__id=station_id,
        equip__equip_model__equip_type__equip_supertype__in=allowed).order_by(
            'equip_id').distinct('equip_id').prefetch_related(
                'equip__equip_model__equip_type__equip_supertype',
                'intervention')

    potential_equipments = [x.equip_id for x in interventions]
    for equip_id in potential_equipments:
        last_station_id = equip_place_todate_id(equip_id, date, None)
        if int(last_station_id) == station_id:
            equipment_list.append(equip_id)
    return Equipment.objects.filter(id__in=equipment_list).prefetch_related(
        'equip_model').order_by('equip_model', 'serial_number')


def xhr_equip_oper(request):
    """
    Request that return the possible scientific equipment in operation for a
    station.
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        station = request.GET.get('station', '')
        date_debut = request.GET.get('date', '')
        heure_debut = request.GET.get('heure', '')

        if not station:
            return HttpResponse(status=400)

        date_heure_channel = u''.join([date_debut, u' ', heure_debut])
        date_debut_channel = datetime.strptime(
            date_heure_channel, "%Y-%m-%d %H:%M:%S")

        equip_dispo = available_equipment_scioper(station, date_debut_channel)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for equip in equip_dispo:
            select_choice.append(({
                "optionValue": equip.id,
                "optionDisplay": str(equip)}))
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def xhr_station_position(request):
    """
    Request that return the position for a station
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        station = request.GET.get('station', '')

        instance = get_object_or_404(StationSite, pk=station)

        select_choice = [{
            "latitude": instance.latitude,
            "longitude": instance.longitude,
            "elevation": instance.elevation}]

        data = json.dumps(select_choice, cls=DecimalEncoder)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


def station_xml(request):
    query = request.GET.get('Station', '')

    aujourdhui = datetime.now()

    result = []

    """Obtain the information about the station """
    ResStation = StationSite.objects.get(pk=query)

    """Obtain the date of creation for this station """
    create_station = None
    intervention_creation = IntervStation.objects.filter(
        intervention__station=query,
        station_action=StationAction.CREER).values('intervention')
    if intervention_creation:
        create_station = Intervention.objects.get(pk=intervention_creation)

    """Obtain the date of closure for this station """
    terminate_station = None
    intervention_terminate = IntervStation.objects.filter(
        intervention__station=query,
        station_action=StationAction.DEMANTELER).values('intervention')
    if intervention_terminate:
        terminate_station = Intervention.objects.get(pk=intervention_terminate)

    """Obtain the channels for that station """
    ResChannel = Channel.objects.filter(
        station_id=query).order_by('-start_date', 'channel_code')

    """Obtain the networks of the channels"""
    ChannelNetwork = Channel.objects.filter(
        station_id=query).distinct('network')

    network_list = [n.network.id for n in ChannelNetwork]

    ResNetwork = Network.objects.filter(id__in=network_list)

    if ResNetwork:
        for network in ResNetwork:
            # Obtain the number of stations for that network
            station_count = Channel.objects.filter(
                network_id=network.id).distinct('station').count()

#            # Obtain the comment for the network
#            ResCommentNetwork = CommentNetwork.objects.filter(
#                network_id=network.id)

            comment_list = []
#            for comment in ResCommentNetwork:
#                # Obtain the authors for each comment
#                ResCommentNetworkAuthor = CommentNetworkAuthor.objects.filter(
#                    comment_network_id=comment.id)
#                comment_list.append([comment, ResCommentNetworkAuthor])

            ResChannels = ResChannel.filter(network_id=network.id)

            station_vault = None
            channel_list = []
            for channel in ResChannels:
                # Obtain the equipment of the chain per channel
                sensor = []
                sensor_installed = None
                sensor_uninstalled = None
                sensor_config = []
                preamplifier = []
                preamplifier_installed = None
                preamplifier_uninstalled = None
                preamplifier_config = []
                datalogger = []
                datalogger_installed = None
                datalogger_uninstalled = None
                datalogger_config = []
                equipment = []
                equipment_installed = None
                equipment_uninstalled = None
                equipment_config = []
                other_1 = []
                other_1_installed = None
                other_1_uninstalled = None
                other_1_config = []
                other_2 = []
                other_2_installed = None
                other_2_uninstalled = None
                other_2_config = []
                other_3 = []
                other_3_installed = None
                other_3_uninstalled = None
                other_3_config = []
                other_4 = []
                other_4_installed = None
                other_4_uninstalled = None
                other_4_config = []
                other_5 = []
                other_5_installed = None
                other_5_uninstalled = None
                other_5_config = []
                ResChain = Chain.objects.filter(channel=channel.id)
                # The type in define in then CHAIN.CHOICES_ORDER
                for equipchain in ResChain:
                    if equipchain.order == Chain.SENSOR:
                        sensor = equipchain.equip
                        # Obtain the config parameters and values for the
                        # sensor
                        sensor_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.PREAMPLIFIER:
                        preamplifier = equipchain.equip
                        # Obtain the config parameters and values for the
                        # preamplifier
                        preamplifier_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.DATALOGGER:
                        datalogger = equipchain.equip
                        # Obtain the config parameters and values for the
                        # datalogger
                        datalogger_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.EQUIPMENT:
                        equipment = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        equipment_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_1:
                        other_1 = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        other_1_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_2:
                        other_2 = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        other_2_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_3:
                        other_3 = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        other_3_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_4:
                        other_4 = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        other_4_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_5:
                        other_5 = equipchain.equip
                        # Obtain the config parameters and values for the
                        # equipment
                        other_5_config = ChainConfig.objects.filter(
                            chain=equipchain.id)
                #    e_name = \
                #        equipchain.equip.equip_model.equip_type
                #    if e_name.equip_type_name == \
                #        u'Vélocimètre' or \
                #        e_name.equip_type_name == \
                #            u'Accéléromètre':
                #        sensor = equipchain.equip
                #        # Obtain the config parameters and values for the
                #        # sensor
                #        sensor_config = \
                #            ChainConfig.objects.filter(chain=equipchain.id)
                #    else:
                #        if e_name.equip_type_name == \
                #            u'Numériseur':
                #            datalogger = equipchain.equip
                #            # Obtain the config parameters and values for the
                #                datalogger
                #            datalogger_config = \
                #                ChainConfig.objects.filter(
                #                    chain=equipchain.id)

                # Common queryset parameters
                equip_operation = IntervEquip.objects.filter(
                    intervention__intervention_date__lte=channel.start_date,
                    intervention__station=channel.station.id,
                    equip_action=EquipAction.INSTALLER,
                    equip_state=EquipState.OPERATION)
                equip_removal = IntervEquip.objects.filter(
                    intervention__intervention_date__gte=channel.start_date,
                    intervention__station=channel.station.id,
                    equip_action=EquipAction.DESINSTALLER)
                if sensor != []:
                    # Sensor in operation during the channel life
                    sensor_operation = equip_operation.filter(
                        equip__id=sensor.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if sensor_operation:
                        # Here we have 0 or 1 occurence
                        sensor_installed = sensor_operation[
                            0].intervention.intervention_date
                    # Sensor removal after the start of the channel life
                    sensor_removal = equip_removal.filter(
                        equip__id=sensor.id).order_by(
                            'intervention__intervention_date')[:1]
                    if sensor_removal:
                        # Here we have 0 or 1 occurence
                        sensor_uninstalled = sensor_removal[
                            0].intervention.intervention_date
                if preamplifier != []:
                    # Preamplifier in operation during the channel life
                    preamplifier_operation = equip_operation.filter(
                        equip__id=preamplifier.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if preamplifier_operation:
                        # Here we have 0 or 1 occurence
                        preamplifier_installed = preamplifier_operation[
                            0].intervention.intervention_date
                    # Preamplifier removal after the start of the channel life
                    preamplifier_removal = equip_removal.filter(
                        equip__id=preamplifier.id).order_by(
                            'intervention__intervention_date')[:1]
                    if preamplifier_removal:
                        """ Here we have 0 or 1 occurence """
                        preamplifier_uninstalled = preamplifier_removal[
                            0].intervention.intervention_date
                if datalogger != []:
                    # Datalogger in operation during the channel life
                    datalogger_operation = equip_operation.filter(
                        equip__id=datalogger.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if datalogger_operation:
                        # Here we have 0 or 1 occurence
                        datalogger_installed = datalogger_operation[
                            0].intervention.intervention_date
                    # Datalogger removal after the start of the channel life
                    datalogger_removal = equip_removal.filter(
                        equip__id=datalogger.id).order_by(
                            'intervention__intervention_date')[:1]
                    if datalogger_removal:
                        # Here we have 0 or 1 occurence
                        datalogger_uninstalled = datalogger_removal[
                            0].intervention.intervention_date
                if equipment != []:
                    # Equipment in operation during the channel life
                    equipment_operation = equip_operation.filter(
                        equip__id=equipment.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if equipment_operation:
                        # Here we have 0 or 1 occurence
                        equipment_installed = equipment_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    equipment_removal = equip_removal.filter(
                        equip__id=equipment.id).order_by(
                            'intervention__intervention_date')[:1]
                    if equipment_removal:
                        # Here we have 0 or 1 occurence
                        equipment_uninstalled = equipment_removal[
                            0].intervention.intervention_date
                if other_1 != []:
                    # Equipment in operation during the channel life
                    other_1_operation = equip_operation.filter(
                        equip__id=other_1.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if other_1_operation:
                        # Here we have 0 or 1 occurence
                        other_1_installed = other_1_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    other_1_removal = equip_removal.filter(
                        equip__id=other_1.id).order_by(
                            'intervention__intervention_date')[:1]
                    if other_1_removal:
                        # Here we have 0 or 1 occurence
                        other_1_uninstalled = other_1_removal[
                            0].intervention.intervention_date
                if other_2 != []:
                    # Equipment in operation during the channel life
                    other_2_operation = equip_operation.filter(
                        equip__id=other_2.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if other_2_operation:
                        # Here we have 0 or 1 occurence
                        other_2_installed = other_2_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    other_2_removal = equip_removal.filter(
                        equip__id=other_2.id).order_by(
                            'intervention__intervention_date')[:1]
                    if other_2_removal:
                        # Here we have 0 or 1 occurence
                        other_2_uninstalled = other_2_removal[
                            0].intervention.intervention_date
                if other_3 != []:
                    # Equipment in operation during the channel life
                    other_3_operation = equip_operation.filter(
                        equip__id=other_3.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if other_3_operation:
                        # Here we have 0 or 1 occurence
                        other_3_installed = other_3_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    other_3_removal = equip_removal.filter(
                        equip__id=other_3.id).order_by(
                            'intervention__intervention_date')[:1]
                    if other_3_removal:
                        # Here we have 0 or 1 occurence
                        other_3_uninstalled = other_3_removal[
                            0].intervention.intervention_date
                if other_4 != []:
                    # Equipment in operation during the channel life
                    other_4_operation = equip_operation.filter(
                        equip__id=other_4.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if other_4_operation:
                        # Here we have 0 or 1 occurence
                        other_4_installed = other_4_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    other_4_removal = equip_removal.filter(
                        equip__id=other_4.id).order_by(
                            'intervention__intervention_date')[:1]
                    if other_4_removal:
                        """ Here we have 0 or 1 occurence """
                        other_4_uninstalled = other_4_removal[
                            0].intervention.intervention_date
                if other_5 != []:
                    # Equipment in operation during the channel life
                    other_5_operation = equip_operation.filter(
                        equip__id=other_5.id).order_by(
                            '-intervention__intervention_date')[:1]
                    if other_5_operation:
                        # Here we have 0 or 1 occurence
                        other_5_installed = other_5_operation[
                            0].intervention.intervention_date
                    # Equipment removal after the start of the channel life
                    other_5_removal = equip_removal.filter(
                        equip__id=other_5.id).order_by(
                            'intervention__intervention_date')[:1]
                    if other_5_removal:
                        # Here we have 0 or 1 occurence
                        other_5_uninstalled = other_5_removal[
                            0].intervention.intervention_date
#                # Obtain the comment for the channel
#                ResCommentChannel = CommentChannel.objects.filter(
#                    channel_id=channel.id)

                comment_list = []
#                for comment in ResCommentChannel:
#                    # Obtain the authors for each comment
#                    ResCommentChannelAuthor = CommentChannelAuthor.\
#                        objects.filter(comment_channel_id=comment.id)
#                    comment_list.append([comment, ResCommentChannelAuthor])

                channel_list.append([
                    channel,
                    sensor,
                    sensor_installed,
                    sensor_uninstalled,
                    sensor_config,
                    preamplifier,
                    preamplifier_installed,
                    preamplifier_uninstalled,
                    preamplifier_config,
                    datalogger,
                    datalogger_installed,
                    datalogger_uninstalled,
                    datalogger_config,
                    equipment,
                    equipment_installed,
                    equipment_uninstalled,
                    equipment_config,
                    other_1,
                    other_1_installed,
                    other_1_uninstalled,
                    other_1_config,
                    other_2,
                    other_2_installed,
                    other_2_uninstalled,
                    other_2_config,
                    other_3,
                    other_3_installed,
                    other_3_uninstalled,
                    other_3_config,
                    other_4,
                    other_4_installed,
                    other_4_uninstalled,
                    other_4_config,
                    other_5,
                    other_5_installed,
                    other_5_uninstalled,
                    other_5_config,
                    comment_list])
                # Obtain the last built for the sensor according with the
                # channel date.
                # WARNING only one built among possibly many
                if sensor != []:
                    channel_s_date = channel.start_date
                    last_equip_place = IntervEquip.objects.filter(
                        intervention__intervention_date__lte=channel_s_date,
                        equip__id=sensor.id,
                        station__id=channel.station.id).order_by(
                            '-intervention__intervention_date')[:1]
                    # Here we have 0 or 1 occurence
                    if last_equip_place:
                        if last_equip_place[0].built:
                            station_vault = last_equip_place[
                                0].built.built_type.built_type_name[4:]
            result.append([
                network,
                comment_list,
                station_count,
                ResStation,
                station_vault,
                ResChannels.count(),
                create_station,
                terminate_station,
                channel_list])

    return render(request, "station_xml.xml", {
        "ResNetwork": result,
        "aujourdhui": aujourdhui,
    }, content_type="application/xhtml+xml")


station_xml = staff_member_required(station_xml)


def xhr_parameter_value(request):
    """
    Request that return the possible value according to the parameter
    """
    if request.is_ajax() and request.method == 'GET':
        parameter = request.GET.get('parameter', '')

        value_dispo = ParameterValue.objects.filter(parameter_id=parameter)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for value in value_dispo:
            select_choice.append(({
                "optionValue": value.id,
                "optionDisplay": str(value)}))
        data = json.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


def site_shortcut(request, code):
    site = StationSite.objects.get(station_code=code)
    url = reverse('admin:gissmo_stationsite_change', args=(site.id,))

    return HttpResponseRedirect(url)


def changemodel_display(modifications, equipment):
    """
    Set modification per channel.
    """
    channels = []
    channel_ids = []
    channel_chain_links = []
    msg = ''

    channel_modifications = {}
    nochannel_modifications = []

    for modif in modifications:
        channel = modif.channel
        if channel is not None and channel not in channels:
            channels.append(channel)
            channel_ids.append(channel.id)
            for chain in channel.chain_set.filter(equip=equipment):
                channel_chain_links.append(chain.id)
        if channel and channel not in channel_modifications:
            channel_modifications[channel] = []
        if modif.channel:
            channel_modifications[channel].append(modif)
        else:
            nochannel_modifications.append(modif)

    if not channels:
        msg = 'No channel found.'
        return [], msg

    # 'if' statement avoids problem with empty list in result
    if nochannel_modifications:
        for channel in channel_modifications:
            channel_modifications[channel] += nochannel_modifications

    return zip(
        channels,
        channel_ids,
        channel_chain_links,
        channel_modifications.values()), msg


def changemodel_compare_params(configs, new_params):
    """
    Make a synthesis about old configuration parameters and new one (regarding
    default value)
    """
    result = []

    def get_default_value(name, parameter_ids):
        return ParameterValue.objects.filter(
            parameter__parameter_name=name,
            parameter_id__in=parameter_ids,
            default_value=True).first() or None

    new_param_ids = [p.id for p in new_params]

    # Browse current configuration
    checked_new_params = []
    channels = []
    for config in configs:
        name = config.parameter.parameter_name
        channel = config.channel
        if channel not in channels:
            channels.append(channel)
        p = get_default_value(name, new_param_ids)
        m = ChangeModelModification.objects.create(
            channel=config.channel,
            name=name,
            old_value=config.value)
        if p:
            m.new_value = p
        m.state = m.get_state()
        m.save()
        checked_new_params.append(p)
        result.append(m)

    # Create modification lines (linked to no channel): new params not
    # present in current ones.
    for channel in channels:
        for param in new_params:
            if param not in checked_new_params:
                name = param.parameter_name
                m = ChangeModelModification.objects.create(
                    channel=channel,
                    name=name,
                    new_value=get_default_value(name, [param.id]))
                m.state = m.get_state()
                m.save()
                result.append(m)
    return result


def changemodel_simulation(equipment, model):
    """
    Take current configuration from given equipment and compare it to given
    model.
    Then return a list of modification objects.
    """
    configs = []
    for chain in equipment.chain_set.all():
        for config in chain.chainconfig_set.all():
            configs.append(config)

    new_params = ParameterEquip.objects.filter(
        equip_model=model.id).prefetch_related(
            'parametervalue_set')

    modifications = changemodel_compare_params(
        configs,
        new_params)

    return modifications


def closechannels(ids, date):
    """
    Channels are considered as closed when "end_date" field is filled in.
    This method add given date to each given channel ID.
    """
    res = []
    if not isinstance(ids, list):
        ids = list(ids)
    for channel_id in ids:
        if not date:
            continue
        if not isinstance(channel_id, int):
            channel_id = int(channel_id)
        channel = Channel.objects.get(pk=channel_id)
        channel.end_date = date
        channel.save()
        res.append(str(channel_id))
    return res


@login_required(login_url='/gissmo/login/')
def closechannels_process(request, form, station_id, context):
    """
    Process form and either return on stationsite change form or raise
    an error.
    """
    url = reverse('admin:gissmo_stationsite_change', args=(station_id,))
    success_message = "Channel(s) successfully closed: %s."
    channel_ids = []
    for key in form:
        name = int(key)
        closing_date = form[key]
        result = closechannels([name], closing_date)
        if result:
            channel_ids.append(key)
    if channel_ids:
        messages.success(
            request,
            success_message % ",".join(channel_ids))
        return redirect(url)

    return render(request, "closechannels_view.html", context)


def createchannels_check_duplicates(channel_dict):
    """
    If similar channels on same period: return True.
    Otherwise False.
    Criteria:
      - channel code
      - location code
      - station_id
      - starting date
    """
    code = channel_dict.get('code', None)
    location = channel_dict.get('location', None)
    date = channel_dict.get('date', None)
    station_id = channel_dict.get('station_id', None)
    network_id = channel_dict.get('network_id', None)

    for axis in ['Z', 'N', 'E']:
        name = code + axis
        same = Channel.objects.filter(
            Q(network_id=network_id) &
            Q(channel_code__channel_code=name) &
            Q(location_code=location) &
            Q(station_id=station_id) &
            Q(start_date__lte=date) &
            (
                Q(end_date__isnull=True) |
                Q(end_date__gte=date)
            )
        )
        if same:
            return True

    return False


@login_required(login_url='/gissmo/login/')
def createchannels_process(request, form, chain_formset, station_id, context):
    """
    Create 3 channels regarding data.
    """
    url = reverse('admin:gissmo_stationsite_change', args=(station_id,))
    success_message = "Channels successfylly created: %s"
    default_sample_rate = {
        'BH': 20,
        'HH': 100,
        'LH': 1,
        'VH': 0.1,
        'UH': 0.01,
        'EL': 100,
        'SH': 50,
        'MH': 5,
        'HN': 100,
        'DP': 500,
        'CH': 500,
        'EH': 100,
    }
    default_azimut = {
        'Z': 0,
        'N': 0,
        'E': 90,
    }
    default_dip = {
        'Z': -90,
        'N': 0,
        'E': 0,
    }
    data = form.cleaned_data
    code = data.get('code')
    date = data.get('date')
    location = data.get('location')
    network = Network.objects.get(pk=data.get('network'))
    station = StationSite.objects.get(pk=station_id)
    created_channels = []

    chain_data = []

    # Check that no duplicates exist
    channel_info = {
        'code': code,
        'date': date,
        'location': location,
        'network_id': network.id,
        'station_id': station_id,
    }
    duplicates = createchannels_check_duplicates(channel_info)
    if duplicates:
        messages.error(
            request,
            'Channels with similar info exist!')
        return render(request, "createchannels_view.html", context)

    for chain_form in chain_formset.forms:
        if not chain_form.is_valid():
            messages.error(
                request,
                'Acquisition chain misinformed!')
            return render(request, "createchannels_view.html", context)

        chain_data.append(chain_form.cleaned_data)

    for axis in ['Z', 'N', 'E']:
        wide_code = '%s%s' % (code, axis)
        channel_code = ChannelCode.objects.filter(
            channel_code=wide_code).first()
        azimut = default_azimut[axis]
        dip = default_dip[axis]
        channel = Channel.objects.create(
            station=station,
            network=network,
            channel_code=channel_code,
            location_code=location,
            latitude=station.latitude,
            longitude=station.longitude,
            elevation=station.elevation,
            depth=0,
            azimuth=azimut,
            dip=dip,
            sample_rate=default_sample_rate[code],
            start_date=date,
        )
        if channel:
            created_channels.append(wide_code)
        for f in chain_data:
            equip_id = f.get('equipment', None)
            order_value = f.get('order', None)
            if not equip_id and not order_value:
                continue
            equipment = Equipment.objects.get(pk=equip_id)
            chain = Chain.objects.create(
                equip=equipment,
                channel=channel,
                order=order_value)
            # Create parameters on Channel
            chain.set_chainconfig_parameters()

    if created_channels:
        messages.success(
            request,
            success_message % ",".join(created_channels))
    return redirect(url)
