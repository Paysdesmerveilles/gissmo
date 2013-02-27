# coding=utf-8

# Create your views here.
import csv
import os.path
import mimetypes
from datetime import datetime
from django.db.models import Q
from models import *
from tools import DecimalEncoder

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import get_model

from django.utils import simplejson
from django.utils.encoding import smart_str

def site_maps(request):
    query = request.GET.get('Station','')
    ResHistStations = []
    ResStationUnique = []
    StationUnique = ''
    Liste = []

    Stations = StationSite.objects.filter(site_type=1)
 
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
        "ResHistStations": ResHistStations, "query": query, "StationUnique": StationUnique, "ResStatTheo": ResStatTheo, "ResStatTest": ResStatTest},
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

    if (not request.user.is_anonymous()) and request.user.is_authenticated() and ((instance.owner.pk == request.user.pk) or (set(instance.owner.groups.all()) == set(request.user.groups.all()))):
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
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]}]
            select_choice.append({"optionValue": StationState.EN_TEST, "optionDisplay": dict(StationState.STATION_STATES)[StationState.EN_TEST]})
        elif int(action) == StationAction.TERMINER_TEST:
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": dict(StationState.STATION_STATES)[StationState.OPERATION]}]
            select_choice.append({"optionValue": StationState.FERMEE, "optionDisplay": dict(StationState.STATION_STATES)[StationState.FERMEE]})   
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

# TODO fonction qui selon equip_action choisi retourne equip_state possible
def xhr_equip_state(request):
    """
    Request that return the possible states for a station according to the action done
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')

        select_choice = [({"optionValue" : c[0], "optionDisplay" : c[1]}) for c in EquipState.EQUIP_STATES]
        select_choice.insert(0, ({"optionValue": '', "optionDisplay": '-- choisir une action en premier --'}))
        if int(action) == EquipAction.ACHETER:
            select_choice = [{"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]}] 
        elif int(action) == EquipAction.TESTER:
            select_choice = [{"optionValue": EquipState.OPERATION, "optionDisplay": EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]}]
            select_choice.append({"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]})
            select_choice.append({"optionValue": EquipState.DISPONIBLE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1]})
            select_choice.append({"optionValue": EquipState.DEFAUT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]})
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.PANNE-1][1]})
        elif int(action) == EquipAction.INSTALLER:
            select_choice = [{"optionValue": EquipState.OPERATION, "optionDisplay": EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]}]
            select_choice.append({"optionValue": EquipState.DEFAUT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]})
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.PANNE-1][1]})
        elif int(action) == EquipAction.DESINSTALLER:
            select_choice = [{"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]}]
            select_choice.append({"optionValue": EquipState.DISPONIBLE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1]})
            select_choice.append({"optionValue": EquipState.DEFAUT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]})
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.PANNE-1][1]})    
        elif int(action) == EquipAction.CONSTATER_DEFAUT:
            select_choice = [{"optionValue": EquipState.DEFAUT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]}]
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.PANNE-1][1]})
        elif int(action) == EquipAction.MAINT_PREV_DISTANTE or int(action) == EquipAction.MAINT_CORR_DISTANTE:
            select_choice = [{"optionValue": EquipState.OPERATION, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]}]
            select_choice.append({"optionValue": EquipState.DEFAUT, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]})
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.PANNE-1][1]}) 
        elif int(action) == EquipAction.MAINT_PREV_SITE or int(action) == EquipAction.MAINT_CORR_SITE:
            select_choice = [{"optionValue": EquipState.DISPONIBLE, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.DISPONIBLE-1][1]}]
            select_choice.append({"optionValue": EquipState.OPERATION, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]})
            select_choice.append({"optionValue": EquipState.DEFAUT, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.DEFAUT-1][1]})
            select_choice.append({"optionValue": EquipState.PANNE, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.PANNE-1][1]}) 
        elif int(action) == EquipAction.EXPEDIER:
            select_choice = [{"optionValue": EquipState.EN_TRANSIT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.EN_TRANSIT-1][1]}]
        elif int(action) == EquipAction.RECEVOIR:
            select_choice = [{"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]}]
        elif int(action) == EquipAction.METTRE_HORS_USAGE:
            select_choice = [{"optionValue": EquipState.HORS_USAGE, "optionDisplay": EquipState.EQUIP_STATES[EquipState.HORS_USAGE-1][1]}]
        elif int(action) == EquipAction.CONSTATER_DISPARITION:
            select_choice = [{"optionValue": EquipState.DISPARU, "optionDisplay": EquipState.EQUIP_STATES[EquipState.DISPARU-1][1]}]
        elif int(action) == EquipAction.RETROUVER:
            select_choice = [{"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]}] 
        elif int(action) == EquipAction.METTRE_AU_REBUT:
            select_choice = [{"optionValue": EquipState.AU_REBUT, "optionDisplay": EquipState.EQUIP_STATES[EquipState.AU_REBUT-1][1]}]
        elif int(action) == EquipAction.AUTRE:
            pass
        else:
            pass
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

def equip_state_todate(equip, date):
    """
    Function to obtain the state of an equipment at a precise moment
    """
    result = 0
    last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date, equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_state:
        for last in last_equip_state:
            result = last.equip_state
    return result

def equip_last_place(equip):
    """
    Function to obtain the last place where an equipment is
    """
    last_equip_place = IntervEquip.objects.filter(equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_place:
        return last_equip_place[0].station
    else:
        return 'Inconnu'

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

def xhr_equipment(request):
    """
    Request that return the possible equipment for a station according to the action done
    equipment available
    equipment on site
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')
        date_intervention=request.GET.get('date', '')
        heure_intervention=request.GET.get('heure', '')
        station=request.GET.get('station', '')

        date_heure_intervention = u''.join([date_intervention,u' ',heure_intervention])
        date_intervention = datetime.strptime(date_heure_intervention,"%Y-%m-%d %H:%M:%S")

        Liste = []
        equipments = Equipment.objects.all()
       # Install only available equip
        if int(action) == EquipAction.INSTALLER:
            for equip in equipments:
                # TODO Obtain the state at moment T
                #Obtain the last state of all equipment
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_state:
                    for last in last_equip_state:
                        Liste.append(last.id)
            equip_dispo = IntervEquip.objects.filter(equip_state=EquipState.DISPONIBLE ,id__in=Liste).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')
       # Receive only equip En transit
        elif int(action) == EquipAction.RECEVOIR:
            for equip in equipments:
                #Obtain the last state of all equipment
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_state:
                    for last in last_equip_state:
                        Liste.append(last.id)
            equip_dispo = IntervEquip.objects.filter(equip_state=EquipState.EN_TRANSIT ,id__in=Liste).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')
       # Retreive only equip Disparu
        elif int(action) == EquipAction.RETROUVER:
            for equip in equipments:
                #Obtain the last state of all equipment
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_state:
                    for last in last_equip_state:
                        Liste.append(last.id)
            equip_dispo = IntervEquip.objects.filter(equip_state=EquipState.DISPARU ,id__in=Liste).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')
       # Corrective maintenance only equip installed in the station in the following state DEFAUT ou PANNE 
        elif int(action) == EquipAction.MAINT_CORR_DISTANTE or int(action) == EquipAction.MAINT_CORR_SITE:
            for equip in equipments:
                #Obtain the last state of all equipment
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_state:
                    for last in last_equip_state:
                        Liste.append(last.id)
            equip_dispo = IntervEquip.objects.filter(Q(equip_state=EquipState.DEFAUT) | Q(equip_state=EquipState.PANNE) ,id__in=Liste, station__id=station).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')
       # Make action only on equip installed in the station
        else:
            for equip in equipments:
                #Obtain the last place of all equipment
                last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_place:
                    for last in last_equip_place:
                        Liste.append(last.id)
       #     print Liste
#            equip_dispo = IntervEquip.objects.filter(id__in=Liste, station__id=station).order_by('-intervention__intervention_date')
            equip_dispo = IntervEquip.objects.filter(id__in=Liste, station__id=station).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')
       #     print station
       #     print equip_dispo
        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
       # select_choice.append(({"optionValue": "", "optionDisplay": "------"}))
        for equip in equip_dispo:
            select_choice.append(({"optionValue": equip.equip.id, "optionDisplay": equip.equip.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

# TODO fonction qui selon equip_action choisi retourne emplacement possible stations, bati, equipement hote

def xhr_station(request):
    """
    Request that return the possible station according to the action done
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')
        date=request.GET.get('date', '')
        station=request.GET.get('station', '')

        station_dispo = StationSite.objects.all().order_by('station_code')
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

       # If action return only one site this is the only choice possible else
       # we have to select a site 
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

def xhr_built(request):
    """
    Request that return the possible built according to the station
    """
    if request.is_ajax() and request.method == 'GET':
        action=request.GET.get('action', '')
        date=request.GET.get('date', '')
        station=request.GET.get('station', '')
        
        #built_dispo = Built.objects.filter(station__id=station).order_by('station_code')
        built_dispo = Built.objects.filter(station__id=station)

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for built in built_dispo:
            select_choice.append(({"optionValue": built.id, "optionDisplay": built.__unicode__()}))
        data = simplejson.dumps(select_choice)

        return HttpResponse(data)
    # If you want to prevent non XHR calls
    else:
        return HttpResponse(status=400)

def xhr_equip_oper(request):
    """
    Request that return the possible equipment in operation for a station 
    """
    # Check that it's an ajax request and that the method is GET
    if request.is_ajax() and request.method == 'GET':
        station=request.GET.get('station', '')

        Liste = []
        equipments = Equipment.objects.all()

        for equip in equipments:
            #Obtain the last place of all equipment
            last_equip_place = IntervEquip.objects.filter(equip__id=equip.id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
            if last_equip_place:
                for last in last_equip_place:
                    Liste.append(last.id)

        equip_dispo = IntervEquip.objects.filter(id__in=Liste, station__id=station).order_by('equip__equip_supertype','equip__equip_type','equip__equip_model','equip__serial_number')

        select_choice = [{"optionValue": "", "optionDisplay": "------"}]
        for equip in equip_dispo:
            select_choice.append(({"optionValue": equip.equip.id, "optionDisplay": equip.equip.__unicode__()}))
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
  CASE WHEN substr(bdmateriel_channel.channel_code,3,1)='2' THEN 'N' 
  WHEN substr(bdmateriel_channel.channel_code,3,1)='3' THEN 'E' 
  ELSE substr(bdmateriel_channel.channel_code,3,1) END AS "Composante", 
  bdmateriel_channel.channel_code AS "Code du canal",
  bdmateriel_stationsite.station_code  AS "Code du site",
  bdmateriel_channel.latitude AS "Latitude",
  bdmateriel_channel.longitude AS "Longitude",
  bdmateriel_channel.elevation AS "Elevation",
  bdmateriel_channel.depth AS "Profondeur",
  bdmateriel_channel.start_date,
  bdmateriel_channel.end_date,
  bdmateriel_channel.dip AS "Dip",
  bdmateriel_channel.azimuth AS "Azimuth",
  bdmateriel_network.network_code AS "Reseau",
  bdmateriel_actor.actor_name AS "Observatoire",
  (SELECT 
    bdmateriel_equipmodel.equip_model_name || '-' || bdmateriel_equipment.serial_number 
   FROM 
    public.bdmateriel_chain,
    public.bdmateriel_equipment,
    public.bdmateriel_equipmodel
   WHERE
    bdmateriel_chain."order" = 1 AND
    bdmateriel_chain.equip_id = bdmateriel_equipment.id AND
    bdmateriel_equipment.equip_model_id = bdmateriel_equipmodel.id AND
    bdmateriel_chain.channel_id = bdmateriel_channel.id
  ) AS "Capteur S/N",
  (SELECT 
    bdmateriel_equipmodel.equip_model_name || '-' || bdmateriel_equipment.serial_number 
   FROM 
    public.bdmateriel_chain,
    public.bdmateriel_equipment,
    public.bdmateriel_equipmodel
   WHERE
    bdmateriel_chain."order" = 2 AND
    bdmateriel_chain.equip_id = bdmateriel_equipment.id AND
    bdmateriel_equipment.equip_model_id = bdmateriel_equipmodel.id AND
    bdmateriel_chain.channel_id = bdmateriel_channel.id
  ) AS "Numeriseur S/N",
  bdmateriel_channel.sample_rate AS "Fréquence"
FROM 
  public.bdmateriel_channel,
  public.bdmateriel_stationsite,
  public.bdmateriel_network,
  public.bdmateriel_actor
WHERE 
  bdmateriel_channel.station_id = bdmateriel_stationsite.id AND
  bdmateriel_channel.network_id = bdmateriel_network.id AND
  bdmateriel_stationsite.operator_id = bdmateriel_actor.id AND
  bdmateriel_stationsite.id = %s
ORDER BY 
  bdmateriel_channel.start_date,
  bdmateriel_channel.location_code,
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

    return render_to_response("station_xml.html", {
    },
         RequestContext(request, {}), mimetype="application/xhtml+xml") 
station_xml = staff_member_required(station_xml)

def station_dataless(request):
    query = request.GET.get('Station','')

    ResStation = StationSite.objects.get(pk=query)

    ResChannel = Channel.objects.filter(station_id=query).order_by('-start_date','channel_code')

    liste_channel = []
    if ResChannel:
        for channel in ResChannel:
            ResChain = Chain.objects.filter(channel_id=channel.id).order_by('-order')
            liste_chain = []
            chain_count = ResChain.count()
            config_count = 0
            config_count_total = 0
            if ResChain:
                for chain in ResChain:
                    ResChainconfig = ChainConfig.objects.filter(chain_id=chain.id)
                    liste_config = []
                    config_count = ResChainconfig.count()
                    config_count_total += config_count
                    if ResChainconfig:
                        for chainconfig in ResChainconfig:
                            liste_config.append(chainconfig)
                    liste_chain.append([chain,liste_config,config_count])
            if config_count_total > chain_count:
                nbr_ligne = config_count_total
            else: 
                nbr_ligne = chain_count

            liste_channel.append([channel,liste_chain,nbr_ligne])

    return render_to_response("station_dataless.html", {
        "query": query, "ResStation": ResStation, "ResChannel": liste_channel,},
         RequestContext(request, {}),)
site_maps = staff_member_required(site_maps)

