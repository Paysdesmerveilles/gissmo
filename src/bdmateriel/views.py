# Create your views here.
from django.db.models import Q
from models import *
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin

from django import forms
from django.forms.fields import DateField
from django.contrib.admin.widgets import AdminDateWidget

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

admin.site.register_view('report/report_station/', report_station)

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

    print query

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

admin.site.register_view('report/report_equip/', report_equip)

def site_maps(request):

    ResHistStations = ''
    ResState = ''
    
#   Stations operationnelles
#    ResHistStations = HistoricStationState.objects.filter(station_state__station_state_name__icontains = u'Op').distinct()

#    L = [Historique.station.id for Historique in ResHistStations]

#    ResStationSite = StationSite.objects.filter(id__in = L).distinct()

#   Stations non operationnelles
#    ResSite = StationSite.objects.exclude(id__in = L).distinct()

#   Stations et sites avec un etat actif date de fin null
    ResHistStations = HistoricStationState.objects.filter(end_date__isnull = True).distinct()

    ResState = StationState.objects.all()

    return render_to_response("site_gmap.html", {
        "ResHistStations": ResHistStations, "ResState": ResState
    },
         RequestContext(request, {}),)
site_maps = staff_member_required(site_maps)

admin.site.register_view('report/site_maps/', site_maps)
# Fin du Test primaire.

