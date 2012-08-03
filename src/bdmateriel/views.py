# coding=utf-8

# Create your views here.
import os.path
import mimetypes
from datetime import datetime
from django.db.models import Q
from models import *

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404, HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.db.models import get_model

from django.utils import simplejson
from django.utils.encoding import smart_str

def site_maps(request):
    query = request.GET.get('Station','')
    ResHistStations = []
    ResState = []
    ResStationUnique = []
    StationUnique = ''
    Liste = []

    Stations = StationSite.objects.all()

    for station in Stations:
        last_station_state = IntervStation.objects.filter(intervention__station=station, station_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        if last_station_state:
            for last in last_station_state:
                Liste.append(last.id)

    ResHistStations = IntervStation.objects.filter(id__in=Liste)

    if query: 
        ResStationUnique = IntervStation.objects.filter(intervention__station=query, station_state__isnull=False).order_by('-intervention__intervention_date')[:1]
        if ResStationUnique:
            for resstationunique in ResStationUnique:
                StationUnique = resstationunique.intervention.station

    return render_to_response("site_gmap.html", {
        "ResHistStations": ResHistStations, "ResState": ResState, "query": query, "StationUnique": StationUnique
    },
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
    mimetypes.init()

    model = get_model(app_label, model_name)
    instance = get_object_or_404(model, pk=identifier)

    if (not request.user.is_anonymous()) and request.user.is_authenticated() and instance.owner.pk == request.user.pk:
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
            select_choice = [{"optionValue": StationState.INSTALLATION, "optionDisplay": StationState.STATION_STATES[StationState.INSTALLATION-1][1]}] 
        elif int(action) == StationAction.OPERER:
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": StationState.STATION_STATES[StationState.OPERATION-1][1]}]
        elif int(action) == StationAction.CONSTATER_DEFAUT:
            select_choice = [{"optionValue": StationState.DEFAUT, "optionDisplay": StationState.STATION_STATES[StationState.DEFAUT-1][1]}]
            select_choice.append({"optionValue": StationState.PANNE, "optionDisplay": StationState.STATION_STATES[StationState.PANNE-1][1]})            
        elif int(action) == StationAction.MAINT_PREV_DISTANTE or int(action) == StationAction.MAINT_CORR_DISTANTE or int(action) == StationAction.MAINT_PREV_SITE or int(action) == StationAction.MAINT_CORR_SITE:
            select_choice = [{"optionValue": StationState.OPERATION, "optionDisplay": StationState.STATION_STATES[StationState.OPERATION-1][1]}]
            select_choice.append({"optionValue": StationState.DEFAUT, "optionDisplay": StationState.STATION_STATES[StationState.DEFAUT-1][1]})
            select_choice.append({"optionValue": StationState.PANNE, "optionDisplay": StationState.STATION_STATES[StationState.PANNE-1][1]})          
        elif int(action) == StationAction.DEMANTELER:
            select_choice = [{"optionValue": StationState.FERMEE, "optionDisplay": StationState.STATION_STATES[StationState.FERMEE-1][1]}]
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
            select_choice = [{"optionValue": EquipState.A_TESTER, "optionDisplay": EquipState.EQUIP_STATES[EquipState.A_TESTER-1][1]}]
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
        elif int(action) == EquipAction.MAINT_PREV_DISTANTE or int(action) == EquipAction.MAINT_CORR_DISTANTE or int(action) == EquipAction.MAINT_PREV_SITE or int(action) == EquipAction.MAINT_CORR_SITE:
            select_choice = [{"optionValue": EquipState.OPERATION, "optionDisplay":  EquipState.EQUIP_STATES[EquipState.OPERATION-1][1]}]
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
        elif int(action) == EquipAction.METTRE_AU_REBUS:
            select_choice = [{"optionValue": EquipState.AU_REBUS, "optionDisplay": EquipState.EQUIP_STATES[EquipState.AU_REBUS-1][1]}]
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
    result = 0
    last_station_state = IntervStation.objects.filter(intervention__station__id=station,station_state__isnull=False).order_by('-intervention__intervention_date')
    if last_station_state:
        for last in last_station_state:
            result = last.station_state
    return result

def equip_last_state(equip):
    """
    Function to obtain the last state of an equipment
    """
    result = 0
    last_equip_state = IntervEquip.objects.filter(equip__id=equip, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_state:
        for last in last_equip_state:
            result = last.equip_state
    return result

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
    result = 0
    last_equip_place = IntervEquip.objects.filter(equip__id=equip, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_place:
        for last in last_equip_place:
            result = last.station
    return result

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
            equip_dispo = IntervEquip.objects.filter(equip_state=EquipState.DISPONIBLE ,id__in=Liste).order_by('-intervention__intervention_date')
       # Receive only equip En transit
        elif int(action) == EquipAction.RECEVOIR:
            for equip in equipments:
                #Obtain the last state of all equipment
                last_equip_state = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, equip_state__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_state:
                    for last in last_equip_state:
                        Liste.append(last.id)
            equip_dispo = IntervEquip.objects.filter(equip_state=EquipState.EN_TRANSIT ,id__in=Liste).order_by('-intervention__intervention_date')
       # Make action only on equip installed in the station
        else:
            for equip in equipments:
                #Obtain the last place of all equipment
                last_equip_place = IntervEquip.objects.filter(intervention__intervention_date__lt=date_intervention, equip__id=equip.id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
                if last_equip_place:
                    for last in last_equip_place:
                        Liste.append(last.id)
       #     print Liste
            equip_dispo = IntervEquip.objects.filter(id__in=Liste, station__id=station).order_by('-intervention__intervention_date')
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
       # Make action only on equip installed in the station
        else:
            station_dispo = StationSite.objects.filter(id=station)

        select_choice = [] 
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

