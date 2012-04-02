# Create your views here.
import os.path
import mimetypes

from django.db.models import Q
from models import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.db.models import get_model
from django.shortcuts import get_object_or_404
from django.shortcuts import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required

from django import forms
from django.forms.fields import DateField
from django.contrib.admin.widgets import AdminDateWidget

from django.utils.encoding import smart_str

class TestForm(forms.Form):
    t = forms.DateField(widget=AdminDateWidget())

def report_station(request):
    query = request.GET.get('Station','')
    ResStationSite = ''
    ResStation = ''
    ResStationActor = ''
    ResActorAccess = ''
    ResStationState = ''
    ResStationCharac = ''
    ResBati = ''
    ResStationEquip = ''

    ResStationSite = StationSite.objects.all()

    if query:
#       Stations qui repondent au critere
        qset = (
            Q(station_code__iexact=query)
        )
        ResStation = StationSite.objects.select_related().filter(qset).distinct()

#       Intervenants 
	L = [station.id for station in ResStation]
        qset = (
            Q(station__id__in = L, end_date__isnull=True)
        )

        ResStationActor = StationActor.objects.filter(qset).distinct()

#       Accessibilite des intervenants
        L_Intervenant = [actor.actor_id for actor in ResStationActor]
        qset = (
            Q(actor__id__in = L_Intervenant)
        )

        ResActorAccess = ActorAccessibility.objects.select_related().filter(qset).distinct()

#       Dernier etat de la station
	L = [station.id for station in ResStation]
        qset = (
            Q(station__id__in = L, end_date__isnull=True)
        )

        ResStationState = HistoricStationState.objects.filter(qset).distinct()

#       Characteristiques actuelles de la station
	L = [station.id for station in ResStation]
        qset = (
            Q(station__id__in = L, end_date__isnull=True)
        )

        ResStationCharac = HistoricStationCharac.objects.filter(qset).distinct()

#       Batis de la station
	L = [station.id for station in ResStation]
        qset = (
            Q(station__id__in = L)
        )

        ResBati = Built.objects.select_related().filter(qset).distinct()

#       Equipements 
	L = [station.id for station in ResStation]
        qset = (
            Q(station__id__in = L, end_date__isnull=True)
        ) 
         
        ResStationEquip = HistoricStationEquip.objects.select_related().filter(qset).distinct()
         
    else:
        results = []
    return render_to_response("report_station.html", {
        "ResStationSite" : ResStationSite,
        "ResStation" : ResStation,
        "ResStationActor" : ResStationActor,
        "ResActorAccess" : ResActorAccess,
        "ResStationState" : ResStationState,
        "ResStationCharac" : ResStationCharac,
        "ResBati" : ResBati,
        "ResStationEquip" : ResStationEquip,
        "query": query
    },
        RequestContext(request, {}),)
report_station = staff_member_required(report_station)

def report_equip(request):
    query = request.GET.get('Equipement','')
    ResEquips = ''
    ResEquip = ''
    ResEquipActor = ''
    ResActorAccess = ''
    ResEquipState = ''
    ResEquipCharac = ''
    ResStationEquip = ''

    ResEquips = Equipment.objects.all()

    if query:
#       Equipement qui repond au critere
        qset = (
            Q(id__iexact=query)
        )
        ResEquip = Equipment.objects.select_related().filter(qset).distinct()

#       Intervenants 
	L = [equip.id for equip in ResEquip]
        qset = (
            Q(equip__id__in = L, end_date__isnull=True)
        )

        ResEquipActor = EquipActor.objects.filter(qset).distinct()

#       Accessibilite des intervenants
        L_Intervenant = [actor.actor_id for actor in ResEquipActor]
        qset = (
            Q(actor__id__in = L_Intervenant)
        )

        ResActorAccess = ActorAccessibility.objects.select_related().filter(qset).distinct()

#       Dernier etat de l'equipement
	L = [equip.id for equip in ResEquip]
        qset = (
            Q(equip__id__in = L, end_date__isnull=True)
        )

        ResEquipState = HistoricEquipState.objects.filter(qset).distinct()

#       Characteristiques actuelles de l'equipement
	L = [equip.id for equip in ResEquip]
        qset = (
            Q(equip__id__in = L, end_date__isnull=True)
        )

        ResEquipCharac = HistoricEquipCharac.objects.filter(qset).distinct()

#       Equipements 
	L = [equip.id for equip in ResEquip]
        qset = (
            Q(equip__id__in = L, end_date__isnull=True)
        ) 
         
        ResStationEquip = HistoricStationEquip.objects.select_related().filter(qset).distinct()
    else:
        results = []
    return render_to_response("report_equip.html", {
        "ResEquips" : ResEquips,
        "ResEquip" : ResEquip,
        "ResEquipActor" : ResEquipActor,
        "ResActorAccess" : ResActorAccess,
        "ResEquipState" : ResEquipState,
        "ResEquipCharac" : ResEquipCharac,
        "ResStationEquip" : ResStationEquip,
        "query": query
    },
        RequestContext(request, {}),)
report_equip = staff_member_required(report_equip)

def site_maps(request):
    query = request.GET.get('Station','')
    ResHistStations = ''
    ResState = ''
    ResStationUnique = ''

#   Stations operationnelles
#    ResHistStations = HistoricStationState.objects.filter(station_state__station_state_name__icontains = u'Op').distinct()

#    L = [Historique.station.id for Historique in ResHistStations]

#    ResStationSite = StationSite.objects.filter(id__in = L).distinct()

#   Stations non operationnelles
#    ResSite = StationSite.objects.exclude(id__in = L).distinct()

#   Stations et sites avec un etat actif date de fin null
    ResHistStations = HistoricStationState.objects.filter(end_date__isnull = True).distinct()

    ResState = StationState.objects.all()

    if query: 
        ResStationUnique = StationSite.objects.get(pk=query)

    return render_to_response("site_gmap.html", {
        "ResHistStations": ResHistStations, "ResState": ResState, "query": query, "ResStationUnique": ResStationUnique
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

# Fin du Test primaire.

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
