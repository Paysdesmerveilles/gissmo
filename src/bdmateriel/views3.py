# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response
from models import EvenementStation, HistoriqueStationSite

def histostation(request):
    query = request.GET.get('q', '')
    query2 = request.GET.get('q2', '')
    query3 = request.GET.get('q3', '')
    queryevent = request.GET.get('Evenement', '')
    ResStation = ''    
    ResEventStation = ''

#       Liste des evenements pour les equipements
    ResEventStation = EvenementStation.objects.all()

    if query or query2 or query3 or queryevent:
#       Stations qui repondent au critere
        ResStation = HistoriqueStationSite.objects.all().select_related()

        if query:
            qset = (
                Q(station__code_station__icontains=query)
            )
            ResStation = ResStation.filter(qset).distinct()

        if query2:
            qset = (
                Q(station__nom_station__icontains=query2)
            )
            ResStation = ResStation.filter(qset).distinct()

        if query3:
            qset = (
                Q(station__nom_site__icontains=query3)
            )
            ResStation = ResStation.filter(qset).distinct()

        if queryevent:
            qset = (
                Q(evenement__description__icontains=queryevent)
            )
            ResStation = ResStation.filter(qset).distinct()

    else:
        results = []
    return render_to_response("histostation.html", {
        "ResStation": ResStation,
        "ResEventStation": ResEventStation,
        "query": query,
        "query2": query2,
        "query3": query3,
        "queryevent": queryevent
    })


