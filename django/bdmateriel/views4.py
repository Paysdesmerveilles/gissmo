# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response
from models import HistoriqueStationSite, StationSite, StationSiteIntervenant, Bati, EquipStationSite, HistoriqueEquip

def station(request):
    query = request.GET.get('Station', '')
    ResStationSite = ''
    ResHistStation = ''
    ResStation = ''
    ResStationSiteIntervenant = ''
    ResBati = ''
    ResEquip = ''
    ResHistEquip = '' 

    ResStationSite = StationSite.objects.all()

    if query:
#       Stations qui repondent au critere
        qset = (
            Q(code_station__icontains=query)
        )
        ResStation = StationSite.objects.filter(qset)

#       Historique de la station qui repond au critere
        qset = (
            Q(station__code_station__icontains=query)
        )
        ResHistStation = HistoriqueStationSite.objects.select_related().filter(qset)

#       Intervenants de la station
	L = [station.id for station in ResStation]

        ResStationSiteIntervenant = StationSiteIntervenant.objects.select_related().filter(station__id__in = L)

#       Batis de la station
        ResBati = Bati.objects.filter(station__id__in = L)

#       Equipements de la station
        ResEquip = EquipStationSite.objects.filter(station__id__in = L)

#       Historique des equipements
        E = [equipement.equipement.id for equipement in ResEquip]
        ResHistEquip = HistoriqueEquip.objects.select_related().filter(equipement__id__in = E)

    else:
        results = []
    return render_to_response("station.html", {
        "ResStationSite": ResStationSite,
        "ResHistStation": ResHistStation,
        "ResStation": ResStation,
        "ResStationSiteIntervenant":ResStationSiteIntervenant,
        "ResBati": ResBati,
        "ResEquip": ResEquip,
        "ResHistEquip": ResHistEquip,
        "query": query
    })


