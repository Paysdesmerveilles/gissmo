# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response
from models import EquipStationSite, StationSite
from views2 import *
from views3 import *
from views4 import *

def stationequip(request):
    query = request.GET.get('Station','')
    ResStationSite = ''
    ResStation = ''
    ResSiteEquip = ''

    ResStationSite = StationSite.objects.all()

    if query:
#       Stations qui repondent au critere
        qset = (
            Q(code_station__icontains=query)
        )
        ResStation = StationSite.objects.select_related().filter(qset).distinct()

#       Equipements 
	L = [station.id for station in ResStation]

        ResSiteEquip = EquipStationSite.objects.filter(station__id__in = L).distinct()
         
    else:
        results = []
    return render_to_response("stationequip.html", {
        "ResStationSite" : ResStationSite,
        "ResStation": ResStation,
        "ResSiteEquip": ResSiteEquip,
        "query": query
    })


