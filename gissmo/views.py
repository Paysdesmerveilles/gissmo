# coding=utf-8

import csv
import os.path
import mimetypes
from datetime import datetime
from operator import itemgetter
from models import *
from tools import DecimalEncoder

from django.db.models import Q
from django.template import loader, Context
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import get_model
from django.utils import simplejson
from django.utils.encoding import smart_str
from django.utils.encoding import force_unicode
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


def site_maps(request):
    query = request.GET.get('Station','')
    ResHistStations = []
    ResStationUnique = []
    StationUnique = ''
    Liste = []

    Stations = StationSite.objects.filter(site_type=1)

    #Obtain the app_label
    content_type = ContentType.objects.get_for_model(StationSite)
    application_label = content_type.app_label

    for station in Stations:
        last_station_state = IntervStation.objects.filter(intervention__station=station, station_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        if last_station_state:
            for last in last_station_state:
                Liste.append(last.id)

    ResStatTest = StationSite.objects.filter(site_type=6)
    ResStatTheo = StationSite.objects.filter(site_type=7)
    ResHistStations = IntervStation.objects.filter(id__in=Liste)

    if query:
        ResStationUnique = IntervStation.objects.filter(intervention__station=query, station_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        if ResStationUnique:
            for resstationunique in ResStationUnique:
                StationUnique = resstationunique.intervention.station

    return render_to_response("site_gmap.html", {
        "ResHistStations": ResHistStations, "query": query, "StationUnique": StationUnique, "ResStatTheo": ResStatTheo, "ResStatTest": ResStatTest, "application_label": application_label,},
         RequestContext(request, {}),)
site_maps = staff_member_required(site_maps)

def itineraire_maps(request):
    query = request.GET.get('Station','')
    ResStationUnique = ''
    Observatoire = ''

    if query:
        ResStationUnique = StationSite.objects.get(pk=query)

#   Un utilisateur ne doit avoir que deux groupes resif et l'observatoire d'attache
    user_group_list = request.user.groups.exclude(name__iexact = "Resif").values_list('name',flat=True)

#   Verification si la liste est vide
#   Le point de depart est l'EOST, si le user n'a pas d'observatoire assigne ou si l'observatoire n'est pas inscrit comme une station
    if user_group_list:
        user_group = user_group_list[0]
    else:
        user_group = 'EOST'

    try:
        Observatoire = StationSite.objects.get(station_code = user_group)
    except StationSite.DoesNotExist:
        Observatoire = StationSite.objects.get(station_code = 'EOST')

    return render_to_response("itineraire_gmap.html", {
        "ResStationUnique": ResStationUnique,
        "Observatoire": Observatoire,
    },
         RequestContext(request, {}),)
itineraire_maps = staff_member_required(itineraire_maps)

def get_file(request, app_label, model_name, field_name, identifier):
    """
    Function that check if the user can open the file and do so
    The request user must not be anonymous, authenticated and be the owner of the file or be in the same group of the owner
    """
    mimetypes.init()

    #Obtain the model on which we work : StationDoc, EquipDoc or EquipModelDoc
    model = get_model(app_label, model_name)

    #Obtain the instance
    instance = get_object_or_404(model, pk=identifier)

    if (not request.user.is_anonymous()) and request.user.is_authenticated():
        # and ((instance.owner.pk == request.user.pk) or (set(instance.owner.groups.all()) == set(request.user.groups.all()))):
        path = getattr(instance, field_name).file.name
        file_name = os.path.basename(path)
        mime_type_guess = mimetypes.guess_type(file_name)
        fsock = open(path,"r")
        if mime_type_guess is not None:
            response = HttpResponse(fsock, mimetype=mime_type_guess[0])
        response['Content-Disposition'] = 'attachment; filename=' + smart_str(file_name)
        return response
    else:
        raise PermissionDenied()

# TODO fonction qui selon station_action choisi retourne station_state possible
def xhr_station_state(request):
    """
    Request that return the possible states for a station according to the action done
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':

        action=request.GET.get('action', '')
        select_choice = [({"optionValue" : c[0], "optionDisplay" : c[1]}) for c in StationState.STATION_STATES]
        select_choice.insert(0, ({"optionValue": '', "optionDisplay": '-- choisir une action en premier --'}))
        if int(action) == StationAction.CREER or int(action) == StationAction.INSTALLER:
            select_choice = [{"optionValue": StationState.INSTALLATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.INSTALLATION]}]
        elif int(action) == StationAction.DEBUTER_TEST:
            select_choice = [{"optionValue": StationState.EN_TEST, "optionDisplay": dict(StationState.STATION_STATES)[StationState.EN_TEST]}]
            select_choice.append({"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]})
        elif int(action) == StationAction.TERMINER_TEST:
            select_choice = [{"optionValue": StationState.FERMEE, "optionDisplay": dict(StationState.STATION_STATES)[StationState.FERMEE]}]
            select_choice.append({"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]})
        elif int(action) == StationAction.OPERER:
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]}]
        elif int(action) == StationAction.CONSTATER_DEFAUT:
            select_choice = [{"optionValue": StationState.DEFAUT, "optionDisplay": dict(StationState.STATION_STATES)[StationState.DEFAUT]}]
            select_choice.append({"optionValue": StationState.PANNE, "optionDisplay": dict(StationState.STATION_STATES)[StationState.PANNE]})
        elif int(action) == StationAction.MAINT_PREV_DISTANTE or int(action) == StationAction.MAINT_CORR_DISTANTE or int(action) == StationAction.MAINT_PREV_SITE or int(action) == StationAction.MAINT_CORR_SITE:
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]}]
            select_choice.append({"optionValue": StationState.DEFAUT, "optionDisplay": dict(StationState.STATION_STATES)[StationState.DEFAUT]})
            select_choice.append({"optionValue": StationState.PANNE, "optionDisplay": dict(StationState.STATION_STATES)[StationState.PANNE]})
        elif int(action) == StationAction.DEMANTELER:
            select_choice = [{"optionValue": StationState.FERMEE, "optionDisplay": dict(StationState.STATION_STATES)[StationState.FERMEE]}]
        elif int(action) == StationAction.AUTRE:
            pass
        else:
            pass
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

def available_equip_state(action):
    """
    Function that return a list of state according to the action via the parameter
    This is use on add_fields section of the IntervEquipInlineFormset and in xhr_equip_state function
    """
    select_choice = [(c[0],c[1]) for c in EquipState.EQUIP_STATES]
    select_choice.insert(0,('','-- choisir une action en premier --'))
    if int(action) == EquipAction.ACHETER:
        select_choice = [(EquipState.A_TESTER, EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1])]
    elif int(action) == EquipAction.TESTER:
        select_choice = [(EquipState.DISPONIBLE, EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1])]
        select_choice.append((EquipState.OPERATION, EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]))
        select_choice.append((EquipState.A_TESTER, EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]))
        select_choice.append((EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]))
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.INSTALLER:
        select_choice = [(EquipState.OPERATION, EquipState.EQUIP_STATES[EquipState.OPERATION-1][1])]
        select_choice.append((EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]))
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.DESINSTALLER:
        select_choice = [(EquipState.A_TESTER, EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1])]
        select_choice.append((EquipState.DISPONIBLE, EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1]))
        select_choice.append((EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]))
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.CONSTATER_DEFAUT:
        select_choice = [(EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1])]
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.MAINT_PREV_DISTANTE or int(action) == EquipAction.MAINT_CORR_DISTANTE:
        select_choice = [(EquipState.OPERATION, EquipState.EQUIP_STATES[EquipState.OPERATION-1][1])]
        select_choice.append((EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]))
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.MAINT_PREV_SITE or int(action) == EquipAction.MAINT_CORR_SITE:
        select_choice = [(EquipState.DISPONIBLE, EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1])]
        select_choice.append((EquipState.OPERATION, EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]))
        select_choice.append((EquipState.DEFAUT, EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]))
        select_choice.append((EquipState.PANNE, EquipState.EQUIP_STATES[EquipState.PANNE-1][1]))
    elif int(action) == EquipAction.EXPEDIER:
        select_choice = [(EquipState.EN_TRANSIT, EquipState.EQUIP_STATES[EquipState.EN_TRANSIT-1][1])]
    elif int(action) == EquipAction.RECEVOIR:
        select_choice = [(EquipState.A_TESTER, EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1])]
        select_choice.append((EquipState.DISPONIBLE, EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1]))
    elif int(action) == EquipAction.METTRE_HORS_USAGE:
        select_choice = [(EquipState.HORS_USAGE, EquipState.EQUIP_STATES[EquipState.HORS_USAGE-1][1])]
    elif int(action) == EquipAction.CONSTATER_DISPARITION:
        select_choice = [(EquipState.DISPARU, EquipState.EQUIP_STATES[EquipState.DISPARU-1][1])]
    elif int(action) == EquipAction.RETROUVER:
        select_choice = [(EquipState.A_TESTER, EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1])]
    elif int(action) == EquipAction.METTRE_AU_REBUT:
        select_choice = [(EquipState.AU_REBUT, EquipState.EQUIP_STATES[EquipState.AU_REBUT-1][1])]
    elif int(action) == EquipAction.AUTRE:
        pass
    else:
        pass
    return select_choice

def xhr_equip_state(request):
    """
    Request that return the possible states for a station according to the action done
    This is use onchange event
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')

        select_choice = [({"optionValue" : c[0], "optionDisplay" : c[1]}) for c in available_equip_state(action)]
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

def station_last_state(station):
    """
    Function to obtain the last state of a station
    """
    last_station_state = IntervStation.objects.filter(intervention__station__id=station,station_state__isnull=False).order_by('-intervention__intervention_date')
    if last_station_state:
        return dict(StationState.STATION_STATES)[last_station_state[0].station_state]
    else:
        return 'Inconnu'

def equip_last_state(equip):
    """
    Function to obtain the last state of an equipment
    """
    last_equip_state = IntervEquip.objects.filter(equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_state:
        return EquipState.EQUIP_STATES[last_equip_state[0].equip_state-1][1]
    else:
        return 'Inconnu'

def equip_state_todate(equip, date, intervention_id):
    """
    Function to obtain the state of an equipment at a precise moment
    """
    result = 0
    if intervention_id:
        """
        Check that the date of the intervention has not changed
        If yes, we must exclude the intervention form the search
        """
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        if date != intervention.intervention_date:
            last_equip_state = IntervEquip.objects.exclude(intervention__pk=intervention_id).filter(intervention__intervention_date__lt=date, equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        else:
            last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
    else:
        last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]

    if last_equip_state:
        for last in last_equip_state:
            result = last.equip_state
    return result

def equip_with_state_todate(date, intervention_id):
    """
    Function to obtain the state of an equipment at a precise moment
    """
    result = 0
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
                last_equip_state = IntervEquip.objects.exclude(intervention__pk=intervention_id).filter(intervention__intervention_date__lt=date, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
            else:
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        else:
            last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]

        if last_equip_state:
            if last_equip_state[0].equip_state == 3:
                liste.append(equip)
    return liste

def equip_last_place(equip):
    """
    Function to obtain the last place where an equipment is
    """
    last_equip_place = IntervEquip.objects.filter(equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_place:
        return last_equip_place[0].station
    else:
        return 'Inconnu'

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
    last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
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
            last_equip_place = IntervEquip.objects.exclude(intervention__pk=intervention_id).filter(intervention__intervention_date__lte=date, equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
        else:
            last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lte=date, equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    else:
        last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lte=date, equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]

    if last_equip_place:
        for last in last_equip_place:
            result = last.station.id
    return result

def available_equipment_cursor(action, station, date, intervention_id):
    from django.db import connection, transaction

    # Check if intervention_id is set to something else put the value 0
    if not intervention_id:
        intervention_id = 0
    else:
        intervention = get_object_or_404(Intervention, pk=intervention_id)
        # Trick : If the date and site have not changed we put 0 as intervention
        # There is no intervention with the ID 0 but we can keep the same code
        if date == intervention.intervention_date and int(station) == intervention.station_id:
            intervention_id = 0

    cursor = connection.cursor()
    """
    Give the last state and station of an equipment
    If the intervention date or time change via the form of the intervention
    we exclude this intervention to permit the change of those fields (date and time)
    """
    cursor.execute('''SELECT equip_id, intervention_date, station_id, equip_state
    FROM (
    SELECT DISTINCT ON (interv.equip_id)
    interv.equip_id, interv.intervention_date, interv.station_id, interv.equip_state
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
    ORDER  BY interv.equip_id, interv.intervention_date DESC) AS it''', [intervention_id, date])

    equipment_list = []
    equipments = Equipment.objects.all()
    # Buy only equip that were never buy in the system

    if int(action) == EquipAction.ACHETER:
        # Obtain all intervention with BUY as action
        equip_purchased = IntervEquip.objects.exclude(intervention__pk=intervention_id).filter(equip_action=EquipAction.ACHETER)
        list_equip_purchased = []
        for equip in equip_purchased:
            list_equip_purchased.append(equip.equip.id)

        # Obtain all equip without BUY action
        nobuy_equipments = Equipment.objects.exclude(id__in=list_equip_purchased)
        for equip in nobuy_equipments:
            equipment_list.append(equip.id)
    # Install only equip DISPONIBLE or No state
    elif int(action) == EquipAction.INSTALLER:
        for row in cursor.fetchall():
            if row[3] == EquipState.DISPONIBLE:
                equipment_list.append(row[0])
    # Receive only equip En transit or No state
    elif int(action) == EquipAction.RECEVOIR:
        for row in cursor.fetchall():
            if row[3] == EquipState.EN_TRANSIT:
                equipment_list.append(row[0])
    # Retreive only equip Disparu
    elif int(action) == EquipAction.RETROUVER:
        for row in cursor.fetchall():
            if row[3] == EquipState.DISPARU:
                equipment_list.append(row[0])
    # Corrective maintenance only equip installed in the station in the following state DEFAUT ou PANNE
    elif int(action) == EquipAction.MAINT_CORR_DISTANTE or int(action) == EquipAction.MAINT_CORR_SITE:
        for row in cursor.fetchall():
            if row[2] == int(station) and (row[3] == EquipState.DEFAUT or row[3] == EquipState.PANNE):
                equipment_list.append(row[0])
    # Make action only on equip installed in the station
    else:
        for row in cursor.fetchall():
            if row[2] == int(station):
                equipment_list.append(row[0])

    equip_dispo = Equipment.objects.filter(id__in=equipment_list).order_by('equip_supertype','equip_type','equip_model','serial_number')
    return equip_dispo

"""
The function available_equipment will be remplaced by available_equipment_cursor for a better response time
"""
def available_equipment(action, station, date, intervention_id):

    # Check if intervention_id is set to something else put the value 0
    if not intervention_id:
        intervention_id = 0

    equipment_list = []
    equipments = Equipment.objects.all()
    # Buy only equip with No state
    if int(action) == EquipAction.ACHETER:
        # Obtain all intervention with BUY as action
        equip_purchased = IntervEquip.objects.exclude(intervention__pk=intervention_id).filter(equip_action=EquipAction.ACHETER)
        list_equip_purchased = []
        for equip in equip_purchased:
            list_equip_purchased.append(equip.equip.id)

        # Obtain all equip without BUY action
        nobuy_equipments = Equipment.objects.exclude(id__in=list_equip_purchased)
        for equip in nobuy_equipments:
            equipment_list.append(equip.id)
    # Install only equip DISPONIBLE or No state
    elif int(action) == EquipAction.INSTALLER:
        for equip in equipments:
            if equip_state_todate(equip.id, date, int(intervention_id)) == EquipState.DISPONIBLE:
                equipment_list.append(equip.id)
    # Receive only equip En transit or No state
    elif int(action) == EquipAction.RECEVOIR:
        for equip in equipments:
            if equip_state_todate(equip.id, date, int(intervention_id)) == EquipState.EN_TRANSIT:
                equipment_list.append(equip.id)
    # Retreive only equip Disparu
    elif int(action) == EquipAction.RETROUVER:
        for equip in equipments:
            if equip_state_todate(equip.id, date, int(intervention_id)) == EquipState.DISPARU:
                equipment_list.append(equip.id)
    # Corrective maintenance only equip installed in the station in the following state DEFAUT ou PANNE
    elif int(action) == EquipAction.MAINT_CORR_DISTANTE or int(action) == EquipAction.MAINT_CORR_SITE:
        for equip in equipments:
            if int(equip_place_todate_id(equip.id, date, int(intervention_id))) == int(station):
                equip_state = equip_state_todate(equip.id, date, int(intervention_id))
                if equip_state == EquipState.DEFAUT or equip_state == EquipState.PANNE:
                    equipment_list.append(equip.id)
    # Make action only on equip installed in the station
    else:
        for equip in equipments:
            if int(equip_place_todate_id(equip.id, date, int(intervention_id))) == int(station):
                equipment_list.append(equip.id)

    equip_dispo = Equipment.objects.filter(id__in=equipment_list).order_by('equip_supertype','equip_type','equip_model','serial_number')
    return equip_dispo

def xhr_equipment(request):
    """
    Request that return the possible equipment for a station according to the action done
    equipment available
    equipment on site
    """

    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')
        station=request.GET.get('station', '')
        date_intervention=request.GET.get('date', '')
        heure_intervention=request.GET.get('heure', '')
        intervention_id=request.GET.get('intervention', '')

        # From : https://docs.djangoproject.com/en/dev/topics/i18n/timezones/#troubleshooting
        date_heure_intervention = u''.join([date_intervention,u' ',heure_intervention])
        date_without_timezone = datetime.strptime(date_heure_intervention,"%Y-%m-%d %H:%M:%S")
        current_timezone = timezone.get_current_timezone()
        date_intervention = date_without_timezone.replace(tzinfo=current_timezone)

        equip_dispo = available_equipment_cursor(action, station, date_intervention, intervention_id)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for equip in equip_dispo:
            select_choice.append(({"optionValue": equip.id, "optionDisplay": equip.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

# TODO fonction qui selon equip_action choisi retourne emplacement possible stations, bati, equipement hote
def available_station(action, station):
    """
    Function that return a queryset of station according to the action and station on which the intervention occur
    This is use on add_fields section of the IntervEquipInlineFormset and in xhr_station function
    """
    # Send equipment somewhere SAV, OSU or Other
    if int(action) == EquipAction.EXPEDIER:
        station_dispo = StationSite.objects.filter(Q(site_type=StationSite.OBSERVATOIRE) | Q(site_type=StationSite.SAV) | Q(site_type=StationSite.AUTRE)).order_by('station_code')
    # Uninstall and put the equip in OSU or in the station of the intervention
    elif int(action) == EquipAction.DESINSTALLER:
        station_dispo = StationSite.objects.filter(site_type=StationSite.OBSERVATOIRE).order_by('station_code')
    # Not able to know where is the equipment
    elif int(action) == EquipAction.CONSTATER_DISPARITION:
        station_dispo = StationSite.objects.filter(site_type=StationSite.NEANT).order_by('station_code')
    # Stop tracking the equipment
    elif int(action) == EquipAction.METTRE_AU_REBUT:
        station_dispo = StationSite.objects.filter(site_type=StationSite.NEANT).order_by('station_code')
    # Out of service but can stay in the station or place to a observatory or nowhere
    elif int(action) == EquipAction.METTRE_HORS_USAGE:
        station_dispo = StationSite.objects.filter(Q(id=station) | Q(site_type=StationSite.OBSERVATOIRE) | Q(site_type=StationSite.NEANT)).order_by('station_code')
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
        action=request.GET.get('action', '')
        station=request.GET.get('station', '')

       # If action return only one site this is the only choice possible else
       # we have to select a site
        station_dispo = available_station(action, station)
        if station_dispo.count() == 1:
            select_choice = []
        else:
            select_choice = [{"optionValue": "", "optionDisplay": "-- choisir un site --"}]
        for station in station_dispo:
            select_choice.append(({"optionValue": station.id, "optionDisplay": station.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

def available_built(station):
    """
    Function that return a queryset of building according to the station on which the action occur
    This is use on add_fields section of the IntervEquipInlineFormset and in xhr_built function
    """
    built_dispo = Built.objects.filter(station__id=station)

    return built_dispo

def xhr_built(request):
    """
    Request that return the possible built according to the station
    """
    if request.is_ajax() and request.method == 'GET':
        station=request.GET.get('station', '')

        built_dispo = available_built(station)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for built in built_dispo:
            select_choice.append(({"optionValue": built.id, "optionDisplay": built.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

def available_equipment_scioper(station, date):
    """
    Function that return a queryset of scientific equipment in place at the station for the date specify
    This is use on add_fields section of the ChainInlineFormset and in xhr_equip_oper function
    """
    equipment_list = []
    # TODO find a better way to filter
    # Not the best way to filter
    # If the supertype name change we have to change the code too
    equipments = Equipment.objects.filter(Q(equip_supertype__equip_supertype_name="01. Scientifique") | Q(equip_supertype__equip_supertype_name="06. Ordinateur"))

    for equip in equipments:
        if int(equip_place_todate_id(equip.id, date, None)) == int(station):
            equipment_list.append(equip.id)

    equip_dispo = Equipment.objects.filter(id__in=equipment_list).order_by('equip_supertype','equip_type__presentation_rank','equip_model','serial_number')
    return equip_dispo

def xhr_equip_oper(request):
    """
    Request that return the possible scientific equipment in operation for a station
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        station=request.GET.get('station', '')
        date_debut=request.GET.get('date', '')
        heure_debut=request.GET.get('heure', '')

        date_heure_channel = u''.join([date_debut,u' ',heure_debut])
        date_debut_channel = datetime.strptime(date_heure_channel,"%Y-%m-%d %H:%M:%S")

        equip_dispo = available_equipment_scioper(station, date_debut_channel)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for equip in equip_dispo:
            select_choice.append(({"optionValue": equip.id, "optionDisplay": equip.__unicode__()}))
        data = simplejson.dumps(select_choice)

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
        station=request.GET.get('station', '')

        instance = get_object_or_404(StationSite, pk=station)

        select_choice = [{"latitude": instance.latitude, "longitude": instance.longitude, "elevation": instance.elevation}]

        data = simplejson.dumps(select_choice, cls=DecimalEncoder)

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

def dataless(request):
    from django.db import connection, transaction
    cursor = connection.cursor()

    query = request.GET.get('Station','')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dataless.csv"'

    cursor.execute('''SELECT
  CASE WHEN substr(gissmo_channel.channel_code,3,1)='2' THEN 'N'
  WHEN substr(gissmo_channel.channel_code,3,1)='3' THEN 'E'
  ELSE substr(gissmo_channel.channel_code,3,1) END AS "Composante",
  gissmo_channel.channel_code AS "Code du canal",
  gissmo_stationsite.station_code  AS "Code du site",
  gissmo_channel.latitude AS "Latitude",
  gissmo_channel.longitude AS "Longitude",
  gissmo_channel.elevation AS "Elevation",
  gissmo_channel.depth AS "Profondeur",
  gissmo_channel.start_date,
  gissmo_channel.end_date,
  gissmo_channel.dip AS "Dip",
  gissmo_channel.azimuth AS "Azimuth",
  gissmo_network.network_code AS "Reseau",
  gissmo_actor.actor_name AS "Observatoire",
  (SELECT
    gissmo_equipmodel.equip_model_name || '-' || gissmo_equipment.serial_number
   FROM
    public.gissmo_chain,
    public.gissmo_equipment,
    public.gissmo_equipmodel
   WHERE
    gissmo_chain."order" = 1 AND
    gissmo_chain.equip_id = gissmo_equipment.id AND
    gissmo_equipment.equip_model_id = gissmo_equipmodel.id AND
    gissmo_chain.channel_id = gissmo_channel.id
  ) AS "Capteur S/N",
  (SELECT
    gissmo_equipmodel.equip_model_name || '-' || gissmo_equipment.serial_number
   FROM
    public.gissmo_chain,
    public.gissmo_equipment,
    public.gissmo_equipmodel
   WHERE
    gissmo_chain."order" = 2 AND
    gissmo_chain.equip_id = gissmo_equipment.id AND
    gissmo_equipment.equip_model_id = gissmo_equipmodel.id AND
    gissmo_chain.channel_id = gissmo_channel.id
  ) AS "Numeriseur S/N",
  gissmo_channel.sample_rate AS "Fréquence"
FROM
  public.gissmo_channel,
  public.gissmo_stationsite,
  public.gissmo_network,
  public.gissmo_actor
WHERE
  gissmo_channel.station_id = gissmo_stationsite.id AND
  gissmo_channel.network_id = gissmo_network.id AND
  gissmo_stationsite.operator_id = gissmo_actor.id AND
  gissmo_stationsite.id = %s
ORDER BY
  gissmo_channel.start_date,
  gissmo_channel.location_code,
  "Composante" DESC
''', [query])
    dictrow = dictfetchall(cursor)
    writer = csv.writer(response)
    writer.writerow(["Composante","Code du canal","Code du site","Latitude", \
                    "Longitude","Elevation","Profondeur","start_date", \
                    "end_date","Dip","Azimuth","Reseau","Observatoire","Capteur S/N", \
                    "Numeriseur S/N","Fréquence"])
    for row in dictrow:
        writer.writerow([row["Composante"],row["Code du canal"],row["Code du site"],row["Latitude"], \
                         row["Longitude"],row["Elevation"],row["Profondeur"],row["start_date"], \
                         row["end_date"],row["Dip"],row["Azimuth"],row["Reseau"],row["Observatoire"], \
                         row["Capteur S/N"],row["Numeriseur S/N"],row["Fréquence"]])
    return response

def station_xml(request):
    query = request.GET.get('Station','')

    aujourdhui = datetime.now()

    result = []

    """Obtain the information about the station """
    ResStation = StationSite.objects.get(pk=query)

    """Obtain the date of creation for this station """
    create_station = None
    intervention_creation = IntervStation.objects.filter(intervention__station=query, station_action=StationAction.CREER).values('intervention')
    if intervention_creation:
        create_station = Intervention.objects.get(pk=intervention_creation)

    """Obtain the date of closure for this station """
    terminate_station = None
    intervention_terminate = IntervStation.objects.filter(intervention__station=query, station_action=StationAction.DEMANTELER).values('intervention')
    if intervention_terminate:
        terminate_station = Intervention.objects.get(pk=intervention_terminate)

    """Obtain the channels for that station """
    ResChannel = Channel.objects.filter(station_id=query).order_by('-start_date','channel_code')

    """Obtain the networks of the channels"""
    ChannelNetwork = Channel.objects.filter(station_id=query).distinct('network')

    network_list = []
    if ChannelNetwork:
        for network in ChannelNetwork:
            network_list.append(network.network.id)

    ResNetwork = Network.objects.filter(id__in=network_list)

    if ResNetwork:
        for network in ResNetwork:
            """ Obtain the number of stations for that network """
            station_count = Channel.objects.filter(network_id=network.id).distinct('station').count()

            """ Obtain the comment for the network """
            ResCommentNetwork = CommentNetwork.objects.filter(network_id=network.id)

            comment_list = []
            for comment in ResCommentNetwork:
                """ Obtain the authors for each comment """
                author_list = []
                ResCommentNetworkAuthor = CommentNetworkAuthor.objects.filter(comment_network_id=comment.id)
                comment_list.append([comment, ResCommentNetworkAuthor])

            ResChannels = ResChannel.filter(network_id=network.id)

            station_vault = None
            channel_list = []
            for channel in ResChannels:
                """Obtain the equipment of the chain per channel """
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
                        """Obtain the config parameters and values for the sensor """
                        sensor_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.PREAMPLIFIER:
                        preamplifier = equipchain.equip
                        """Obtain the config parameters and values for the preamplifier """
                        preamplifier_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.DATALOGGER:
                        datalogger = equipchain.equip
                        """Obtain the config parameters and values for the datalogger """
                        datalogger_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.EQUIPMENT:
                        equipment = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        equipment_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_1:
                        other_1 = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        other_1_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_2:
                        other_2 = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        other_2_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_3:
                        other_3 = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        other_3_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_4:
                        other_4 = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        other_4_config = ChainConfig.objects.filter(chain=equipchain.id)
                    if equipchain.order == Chain.OTHER_5:
                        other_5 = equipchain.equip
                        """Obtain the config parameters and values for the equipment """
                        other_5_config = ChainConfig.objects.filter(chain=equipchain.id)
                #    if equipchain.equip.equip_type.equip_type_name == u'Vélocimètre' or equipchain.equip.equip_type.equip_type_name == u'Accéléromètre':
                #        sensor = equipchain.equip
                #        """Obtain the config parameters and values for the sensor """
                #        sensor_config = ChainConfig.objects.filter(chain=equipchain.id)
                #    else:
                #        if equipchain.equip.equip_type.equip_type_name == u'Numériseur':
                #            datalogger = equipchain.equip
                #            """Obtain the config parameters and values for the datalogger """
                #            datalogger_config = ChainConfig.objects.filter(chain=equipchain.id)
                """ Common queryset parameters """
                equip_operation = IntervEquip.objects.filter(intervention__intervention_date__lte=channel.start_date, intervention__station=channel.station.id, equip_action=EquipAction.INSTALLER, equip_state=EquipState.OPERATION)
                equip_removal = IntervEquip.objects.filter(intervention__intervention_date__gte=channel.start_date, intervention__station=channel.station.id, equip_action=EquipAction.DESINSTALLER)
                if sensor != []:
                    """ Sensor in operation during the channel life """
                    sensor_operation = equip_operation.filter(equip__id=sensor.id).order_by('-intervention__intervention_date')[:1]
                    if sensor_operation:
                         """ Here we have 0 or 1 occurence """
                         sensor_installed = sensor_operation[0].intervention.intervention_date
                    """ Sensor removal after the start of the channel life """
                    sensor_removal = equip_removal.filter(equip__id=sensor.id).order_by('intervention__intervention_date')[:1]
                    if sensor_removal:
                         """ Here we have 0 or 1 occurence """
                         sensor_uninstalled = sensor_removal[0].intervention.intervention_date
                if preamplifier != []:
                    """ Preamplifier in operation during the channel life """
                    preamplifier_operation = equip_operation.filter(equip__id=preamplifier.id).order_by('-intervention__intervention_date')[:1]
                    if preamplifier_operation:
                        """ Here we have 0 or 1 occurence """
                        preamplifier_installed = preamplifier_operation[0].intervention.intervention_date
                    """ Preamplifier removal after the start of the channel life """
                    preamplifier_removal = equip_removal.filter(equip__id=preamplifier.id).order_by('intervention__intervention_date')[:1]
                    if preamplifier_removal:
                         """ Here we have 0 or 1 occurence """
                         preamplifier_uninstalled = preamplifier_removal[0].intervention.intervention_date
                if datalogger != []:
                    """ Datalogger in operation during the channel life """
                    datalogger_operation = equip_operation.filter(equip__id=datalogger.id).order_by('-intervention__intervention_date')[:1]
                    if datalogger_operation:
                        """ Here we have 0 or 1 occurence """
                        datalogger_installed = datalogger_operation[0].intervention.intervention_date
                    """ Datalogger removal after the start of the channel life """
                    datalogger_removal = equip_removal.filter(equip__id=datalogger.id).order_by('intervention__intervention_date')[:1]
                    if datalogger_removal:
                         """ Here we have 0 or 1 occurence """
                         datalogger_uninstalled = datalogger_removal[0].intervention.intervention_date
                if equipment != []:
                    """ Equipment in operation during the channel life """
                    equipment_operation = equip_operation.filter(equip__id=equipment.id).order_by('-intervention__intervention_date')[:1]
                    if equipment_operation:
                        """ Here we have 0 or 1 occurence """
                        equipment_installed = equipment_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    equipment_removal = equip_removal.filter(equip__id=equipment.id).order_by('intervention__intervention_date')[:1]
                    if equipment_removal:
                         """ Here we have 0 or 1 occurence """
                         equipment_uninstalled = equipment_removal[0].intervention.intervention_date
                if other_1 != []:
                    """ Equipment in operation during the channel life """
                    other_1_operation = equip_operation.filter(equip__id=other_1.id).order_by('-intervention__intervention_date')[:1]
                    if other_1_operation:
                        """ Here we have 0 or 1 occurence """
                        other_1_installed = other_1_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    other_1_removal = equip_removal.filter(equip__id=other_1.id).order_by('intervention__intervention_date')[:1]
                    if other_1_removal:
                         """ Here we have 0 or 1 occurence """
                         other_1_uninstalled = other_1_removal[0].intervention.intervention_date
                if other_2 != []:
                    """ Equipment in operation during the channel life """
                    other_2_operation = equip_operation.filter(equip__id=other_2.id).order_by('-intervention__intervention_date')[:1]
                    if other_2_operation:
                        """ Here we have 0 or 1 occurence """
                        other_2_installed = other_2_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    other_2_removal = equip_removal.filter(equip__id=other_2.id).order_by('intervention__intervention_date')[:1]
                    if other_2_removal:
                         """ Here we have 0 or 1 occurence """
                         other_2_uninstalled = other_2_removal[0].intervention.intervention_date
                if other_3 != []:
                    """ Equipment in operation during the channel life """
                    other_3_operation = equip_operation.filter(equip__id=other_3.id).order_by('-intervention__intervention_date')[:1]
                    if other_3_operation:
                        """ Here we have 0 or 1 occurence """
                        other_3_installed = other_3_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    other_3_removal = equip_removal.filter(equip__id=other_3.id).order_by('intervention__intervention_date')[:1]
                    if other_3_removal:
                         """ Here we have 0 or 1 occurence """
                         other_3_uninstalled = other_3_removal[0].intervention.intervention_date
                if other_4 != []:
                    """ Equipment in operation during the channel life """
                    other_4_operation = equip_operation.filter(equip__id=other_4.id).order_by('-intervention__intervention_date')[:1]
                    if other_4_operation:
                        """ Here we have 0 or 1 occurence """
                        other_4_installed = other_4_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    other_4_removal = equip_removal.filter(equip__id=other_4.id).order_by('intervention__intervention_date')[:1]
                    if other_4_removal:
                         """ Here we have 0 or 1 occurence """
                         other_4_uninstalled = other_4_removal[0].intervention.intervention_date
                if other_5 != []:
                    """ Equipment in operation during the channel life """
                    other_5_operation = equip_operation.filter(equip__id=other_5.id).order_by('-intervention__intervention_date')[:1]
                    if other_5_operation:
                        """ Here we have 0 or 1 occurence """
                        other_5_installed = other_5_operation[0].intervention.intervention_date
                    """ Equipment removal after the start of the channel life """
                    other_5_removal = equip_removal.filter(equip__id=other_5.id).order_by('intervention__intervention_date')[:1]
                    if other_5_removal:
                         """ Here we have 0 or 1 occurence """
                         other_5_uninstalled = other_5_removal[0].intervention.intervention_date
                """ Obtain the comment for the channel """
                ResCommentChannel = CommentChannel.objects.filter(channel_id=channel.id)

                comment_list = []
                for comment in ResCommentChannel:
                    """ Obtain the authors for each comment """
                    author_list = []
                    ResCommentChannelAuthor = CommentChannelAuthor.objects.filter(comment_channel_id=comment.id)
                    comment_list.append([comment, ResCommentChannelAuthor])

                channel_list.append([channel, sensor, sensor_installed, sensor_uninstalled, sensor_config, \
                                     preamplifier, preamplifier_installed, preamplifier_uninstalled, preamplifier_config, \
                                     datalogger, datalogger_installed, datalogger_uninstalled, datalogger_config, \
                                     equipment, equipment_installed, equipment_uninstalled, equipment_config, \
                                     other_1, other_1_installed, other_1_uninstalled, other_1_config, \
                                     other_2, other_2_installed, other_2_uninstalled, other_2_config, \
                                     other_3, other_3_installed, other_3_uninstalled, other_3_config, \
                                     other_4, other_4_installed, other_4_uninstalled, other_4_config, \
                                     other_5, other_5_installed, other_5_uninstalled, other_5_config, \
                                     comment_list])
                """ Obtain the last built for the sensor according with the channel date """
                """ WARNING only one built among possibly many """
                if sensor != []:
                    last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lte=channel.start_date, equip__id=sensor.id, station__id=channel.station.id).order_by('-intervention__intervention_date')[:1]
                    """ Here we have 0 or 1 occurence """
                    if last_equip_place:
                        if last_equip_place[0].built:
                            station_vault = last_equip_place[0].built.built_type.built_type_name[4:]
            result.append([network, comment_list, station_count, ResStation, station_vault, ResChannels.count(), create_station, terminate_station, channel_list])

    return render_to_response("station_xml.xml", {
    "ResNetwork": result, "aujourdhui": aujourdhui },
         RequestContext(request, {}), mimetype="application/xhtml+xml")
station_xml = staff_member_required(station_xml)

def network_xml(request):
    response = HttpResponse(mimetype='application/xhtml+xml')
    response['Content-Disposition'] = 'attachment; filename="somefilename.xhtml"'

    query = request.GET.get('Network','')

    result = []

    """Obtain the information about the network """
    network = Network.objects.get(pk=query)

    if network:
            """ Obtain the stations for that network """
            ResStations = Channel.objects.filter(network_id=network.id).distinct('station').order_by('station.station_code')

            """ Obtain the number of stations for that network """
            station_count = ResStations.count()

            station_list = []
            if ResStations:
                for station in ResStations:
                    """Obtain the information about the station """
                    ResStation = StationSite.objects.get(pk=station.station_id)

                    """Obtain the date of creation for this station """
                    create_station = None
                    intervention_creation = IntervStation.objects.filter(intervention__station=ResStation.id, station_action=StationAction.CREER).values('intervention')
                    if intervention_creation:
                        create_station = Intervention.objects.get(pk=intervention_creation)

                    """Obtain the date of closure for this station """
                    terminate_station = None
                    intervention_terminate = IntervStation.objects.filter(intervention__station=ResStation.id, station_action=StationAction.DEMANTELER).values('intervention')
                    if intervention_terminate:
                        terminate_station = Intervention.objects.get(pk=intervention_terminate)

                    """Obtain the channels for that station """
                    ResChannels = Channel.objects.filter(station_id=ResStation.id,network_id=network.id).order_by('-start_date','channel_code')

                    station_vault = None

                    channel_list = []
                    for channel in ResChannels:
                        """Obtain the equipment of the chain per channel """
                        sensor = []
                        sensor_installed = None
                        sensor_uninstalled = None
                        preamplifier = []
                        preamplifier_installed = None
                        preamplifier_uninstalled = None
                        datalogger = []
                        datalogger_installed = None
                        datalogger_uninstalled = None
                        ResChain = Chain.objects.filter(channel=channel.id)
                        for equipchain in ResChain:
                            if equipchain.equip.equip_type.equip_type_name == u'Vélocimètre' or equipchain.equip.equip_type.equip_type_name == u'Accéléromètre':
                                sensor = equipchain.equip
                            else:
                                if equipchain.equip.equip_type.equip_type_name == u'Numériseur':
                                    datalogger = equipchain.equip
                        """ Common queryset parameters """
                        equip_operation = IntervEquip.objects.filter(intervention__intervention_date__lte=channel.start_date, intervention__station=channel.station.id, equip_action=EquipAction.INSTALLER,        equip_state=EquipState.OPERATION)
                        equip_removal = IntervEquip.objects.filter(intervention__intervention_date__gte=channel.start_date, intervention__station=channel.station.id, equip_action=EquipAction.DESINSTALLER)
                        if sensor != []:
                            """ Sensor in operation during the channel life """
                            sensor_operation = equip_operation.filter(equip__id=sensor.id).order_by('-intervention__intervention_date')[:1]
                            if sensor_operation:
                                 """ Here we have 0 or 1 occurence """
                                 sensor_installed = sensor_operation[0].intervention.intervention_date
                            """ Sensor removal after the start of the channel life """
                            sensor_removal = equip_removal.filter(equip__id=sensor.id).order_by('intervention__intervention_date')[:1]
                            if sensor_removal:
                                 """ Here we have 0 or 1 occurence """
                                 sensor_uninstalled = sensor_removal[0].intervention.intervention_date
                        if preamplifier != []:
                            """ Preamplifier in operation during the channel life """
                            preamplifier_operation = equip_operation.filter(equip__id=preamplifier.id).order_by('-intervention__intervention_date')[:1]
                            if preamplifier_operation:
                                """ Here we have 0 or 1 occurence """
                                preamplifier_installed = preamplifier_operation[0].intervention.intervention_date
                            """ Preamplifier removal after the start of the channel life """
                            preamplifier_removal = equip_removal.filter(equip__id=preamplifier.id).order_by('intervention__intervention_date')[:1]
                            if preamplifier_removal:
                                 """ Here we have 0 or 1 occurence """
                                 preamplifier_uninstalled = preamplifier_removal[0].intervention.intervention_date
                        if datalogger != []:
                            """ Datalogger in operation during the channel life """
                            datalogger_operation = equip_operation.filter(equip__id=datalogger.id).order_by('-intervention__intervention_date')[:1]
                            if datalogger_operation:
                                """ Here we have 0 or 1 occurence """
                                datalogger_installed = datalogger_operation[0].intervention.intervention_date
                            """ Datalogger removal after the start of the channel life """
                            datalogger_removal = equip_removal.filter(equip__id=datalogger.id).order_by('intervention__intervention_date')[:1]
                            if datalogger_removal:
                                 """ Here we have 0 or 1 occurence """
                                 datalogger_uninstalled = datalogger_removal[0].intervention.intervention_date

                        """ Obtain the comment for the channel """
                        ResCommentChannel = CommentChannel.objects.filter(channel_id=channel.id)

                        comment_list = []
                        for comment in ResCommentChannel:
                            """ Obtain the authors for each comment """
                            author_list = []
                            ResCommentChannelAuthor = CommentChannelAuthor.objects.filter(comment_channel_id=comment.id)
                            comment_list.append([comment, ResCommentChannelAuthor])

                        channel_list.append([channel, sensor, sensor_installed, sensor_uninstalled, preamplifier, preamplifier_installed, preamplifier_uninstalled, datalogger, datalogger_installed, datalogger_uninstalled, comment_list])
                    station_list.append([ResStation, station_vault, ResChannels.count(), create_station, terminate_station, channel_list])

            """ Obtain the comment for the network """
            ResCommentNetwork = CommentNetwork.objects.filter(network_id=network.id)

            comment_list = []
            for comment in ResCommentNetwork:
                """ Obtain the authors for each comment """
                author_list = []
                ResCommentNetworkAuthor = CommentNetworkAuthor.objects.filter(comment_network_id=comment.id)
                comment_list.append([comment, ResCommentNetworkAuthor])
            result.append([network, comment_list, station_count, station_list])
#            result.append([network, comment_list, station_count, ResStation, station_vault, ResChannels.count(), create_station, terminate_station, channel_list])

#    return render_to_response("network_xml.xml", {
#    "ResNetwork": result,},
#         RequestContext(request, {}), mimetype="application/xhtml+xml")
    t = loader.get_template('network_xml.xml')
    c = Context({
        "ResNetwork": result,
    })
    response.write(t.render(c))
    return response
#    return render_to_string("network_xml.xml", {
#    "ResNetwork": result,},
#         RequestContext(request, {}))
#network_xml = staff_member_required(network_xml)

def station_dataless(request):
    query = request.GET.get('Station','')

    ResStation = StationSite.objects.get(pk=query)

    ResChannel = Channel.objects.filter(station_id=query).extra(select={'component': "SUBSTR(channel_code, LENGTH(channel_code)-1, LENGTH(channel_code))",'channel':"SUBSTR(channel_code, 1, LENGTH(channel_code)-1)"}).order_by('-start_date','channel','-component')

    """ New to accomodate PANDORA interface """
    sensor_list = []
    datalogger_list =[]
    liste_channel = []
    liste_canaux = []

    prev_channel_component = []
    liste_voies = []
    liste_azimuth = []
    liste_dip = []
    liste_component = []
    channel_prec = []
    liste_canal_prec = []
    if ResChannel:
        for channel in ResChannel:
            channel_component = [channel.network, channel.station, channel.location_code, channel.channel_code[:2], channel.sample_rate, channel.start_date, channel.end_date]

            ResChain = Chain.objects.filter(channel_id=channel.id).order_by('order')
            liste_chain = []
            if ResChain:
                for chain in ResChain:
                    ResChainconfig = ChainConfig.objects.filter(chain_id=chain.id)
                    liste_config = []
                    if ResChainconfig:
                        for chainconfig in ResChainconfig:
                            liste_config.append(chainconfig)
                    liste_chain.append([chain.equip,liste_config])
                    """ Built of the sensor and dataloger list """
                    if chain.equip.equip_type.equip_type_name == u'Vélocimètre' or chain.equip.equip_type.equip_type_name == u'Accéléromètre':
                        sensor_list.append(chain.equip)
                    else:
                        if chain.equip.equip_type.equip_type_name == u'Numériseur':
                            datalogger_list.append(chain.equip)

            liste_channel.append([channel,liste_chain])

            liste_canal = [channel_component, liste_chain]
            if liste_canal_prec != liste_canal:
                 """ First time initialisation """
                 if liste_canal_prec != []:
                     liste_canaux.append([channel_prec, liste_canal_prec[1], liste_component, liste_azimuth, liste_dip])
                     liste_azimuth = []
                     liste_dip = []
                     liste_component = []
                 liste_canal_prec = liste_canal
                 channel_prec = channel
            liste_azimuth.append(channel.azimuth)
            liste_dip.append(channel.dip)
            liste_component.append(channel.channel_code[2:])

        liste_canaux.append([channel_prec, liste_canal_prec[1], liste_component, liste_azimuth, liste_dip])

    return render_to_response("station_dataless.html", {
        "query": query, "ResStation": ResStation, "SensorList": list(set(sensor_list)), "DataloggerList": list(set(datalogger_list)), "ResChannel": liste_canaux,},
         RequestContext(request, {}),)
site_maps = staff_member_required(site_maps)

def test_site(request):
    from django.db import connection, transaction
    cursor = connection.cursor()

    query = request.GET.get('Station','')
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="test_site.csv"'

    cursor.execute('''SELECT DISTINCT
  gissmo_stationsite.station_code AS "Code du site",
  gissmo_stationsite.site_name AS "Nom du site",
  gissmo_stationsite.address AS "Adresse",
  gissmo_stationsite.town AS "Commune",
  gissmo_stationsite.county AS "Departement",
  gissmo_stationsite.region AS "Region",
  gissmo_stationsite.country AS "Pays",
  gissmo_stationsite.latitude AS "Latitude",
  gissmo_stationsite.longitude AS "Longitude",
  gissmo_stationsite.note AS "Note",
  gissmo_stationdoc.private_link AS "Lien vers document prive",
  (SELECT gissmo_stationstate.station_state_name
   FROM
      public.gissmo_intervention,
      public.gissmo_intervstation,
      public.gissmo_stationstate
   WHERE
      gissmo_intervention.station_id = gissmo_stationsite.id AND
      gissmo_intervstation.intervention_id = gissmo_intervention.id AND
      gissmo_intervstation.station_state IS NOT NULL AND
      gissmo_intervstation.station_state = gissmo_stationstate.id
   ORDER BY
      gissmo_intervention.intervention_date DESC
   LIMIT 1) AS "Etat",
   (SELECT gissmo_actor.actor_name
    FROM
       gissmo_actor
    WHERE
       gissmo_stationsite.operator_id = gissmo_actor.id) AS "Operateur"
FROM
  public.gissmo_stationsite LEFT JOIN public.gissmo_stationdoc ON (gissmo_stationdoc.station_id = gissmo_stationsite.id)
WHERE
  gissmo_stationsite.site_type = 6
ORDER BY
  gissmo_stationsite.station_code
''', [query])
    dictrow = dictfetchall(cursor)
    writer = csv.writer(response)
    writer.writerow(["Code du site","Nom du site","Adresse", \
                    "Commune","Departement","Region","Pays", \
                    "Latitude","Longitude","Note","Lien vers document prive","Etat","Operateur"])
    for row in dictrow:
        writer.writerow([unicode(s).encode("utf-8") for s in (
                         row["Code du site"],row["Nom du site"],row["Adresse"],row["Commune"], \
                         row["Departement"],row["Region"],row["Pays"],row["Latitude"], \
                         row["Longitude"],row["Note"],row["Lien vers document prive"],row["Etat"],row["Operateur"])])
    return response
"""
from pghstore import loads

def test_dbchange(request):
    asking_date = request.GET.get('Date','')

    asking_datehour = u''.join([asking_date,u' ',"00:00:00"])

    ResChange = LoggedActions.objects.filter(action_tstamp_tx__lt=datetime.strptime(asking_datehour,"%Y-%m-%d %H:%M:%S")).order_by('action_tstamp_tx')

    response = HttpResponse(mimetype='text/plain')
    response['Content-Disposition'] = 'attachment; filename="dbchange.txt"'

    for change in ResChange:
        # Insert
        response.write("Table name    : %s \n" % change.table_name)
        response.write("Date    : %s" % change.action_tstamp_tx)
        response.write("\n")
        if change.action == "I":
            response.write("Table action  : Insert\n")
            response.write("Changed value : %-30s : %-30s\n" % ("FIELDS","VALUES"))
            for key, value in loads(change.row_data).items():
                response.write("                %-30s : %-30s\n" % (key, value))
            response.write("\n")
        else:
            # Delete
            if change.action == "D":
                response.write("Table action  : Delete\n")
                response.write("Changed value : %-30s : %-30s\n" % ("FIELDS","VALUES"))
                for key, value in loads(change.row_data).items():
                    response.write("                %-30s : %-30s\n" % (key, value))
                response.write("\n")
            else:
                # Update
                if change.action == "U":
                    response.write("Table action  : Update\n")
                    response.write("Changed value : %-30s : %-30s\n" % ("FIELDS","VALUES"))
                    for key, value in loads(change.changed_fields).items():
                        response.write("                %-30s : %-30s\n" % (key, value))
                    response.write("\n")
                # Other action
                else:
                    response.write("Other\n")
        response.write("\n")
    return response
"""

def xhr_parameter_value(request):
    """
    Request that return the possible value according to the parameter
    """
    if request.is_ajax() and request.method == 'GET':
        parameter=request.GET.get('parameter', '')

        value_dispo = ParameterValue.objects.filter(parameter_id=parameter)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for value in value_dispo:
            select_choice.append(({"optionValue": value.id, "optionDisplay": value.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)


#
#
#  Ne pas oublier de mettre en place
#
#        Audit_trigger_91plus
#
#
# Pour donner acces a la table d'audit logged_actions dans le schema audit
# il faut modifier le role du user de l'aplplication Django (bdmateriel - Gissmo)
#
#        ALTER ROLE martin SET SEARCH_PATH to "$user",public,audit;
#
# Il faut ajouter le module pghstore pour convertir un champ hstore
# dans un dictionnaire python
#
# This small module implements a formatter and a loader for hstore
#
#         pip install pghstore
#
