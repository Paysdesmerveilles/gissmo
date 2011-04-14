# Create your views here.
from django.db.models import Q
from django.shortcuts import render_to_response
from models import CategorieEquip, Intervenant, EvenementEquip, HistoriqueEquip, EquipStationSite

def histoequip(request):
    querycat = request.GET.get('Categorie', '')
    querycons = request.GET.get('Constructeur', '')
    queryfourn = request.GET.get('Fournisseur', '')
    query = request.GET.get('q', '')
    query2 = request.GET.get('q2', '')
    queryevent = request.GET.get('Evenement', '')
    ResCatgEquip = ''
    ResCons = ''
    ResFourn = ''
    ResEventEquip = ''
    ResEquip = ''    
    ResEquipStationSite = ''


#       Liste des categories pour les equipements
    ResCatgEquip = CategorieEquip.objects.all()

#       Liste des constructeurs
    qset = (
        Q(categorie__nom__icontains='constructeur')
        )
    ResCons = Intervenant.objects.filter(qset).distinct()

#       Liste des fournisseurs
    qset = (
        Q(categorie__nom__icontains='fournisseur')
        )
    ResFourn = Intervenant.objects.filter(qset).distinct()

#       Liste des evenements pour les equipements
    ResEventEquip = EvenementEquip.objects.all()

    if querycat or querycons or queryfourn or query or query2 or queryevent:
#       Stations qui repondent au critere
        ResEquip = HistoriqueEquip.objects.all().select_related()
        if querycat:
            qset = (
                Q(equipement__categorie__nom__icontains=querycat)
            )
            ResEquip = HistoriqueEquip.objects.filter(qset).distinct()

        if querycons:
            qset = (
                Q(equipement__constructeur__nom__icontains=querycons)
            )
            ResEquip = ResEquip.filter(qset).distinct()

        if queryfourn:
            qset = (
                Q(equipement__fournisseur__nom__icontains=queryfourn)
            )
            ResEquip = ResEquip.filter(qset).distinct()

        if query:
            qset = (
                Q(equipement__modele__icontains=query)
            )
            ResEquip = ResEquip.filter(qset).distinct()

        if query2:
            qset = (
                Q(equipement__no_serie__icontains=query2)
            )
            ResEquip = ResEquip.filter(qset).distinct()

        if queryevent:
            qset = (
                Q(evenement__description__icontains=queryevent)
            )
            ResEquip = ResEquip.filter(qset).distinct()

        #       Emplacements des equipements
	L = [equipement.equipement.id for equipement in ResEquip]

        ResEquipStationSite = EquipStationSite.objects.select_related().distinct().filter(equipement__id__in = L)

#        if query and query2:
#            qset = (
#                (Q(equipement__modele__icontains=query) & Q(equipement__no_serie__icontains=query2))
#            )
#            ResEquip = HistoriqueEquip.objects.filter(qset).distinct()
#        else:
#            if query:
#                qset = (
#                    Q(equipement__modele__icontains=query) 
#                )
#            else:
#                qset = (
#                    Q(equipement__no_serie__icontains=query2)
#                )
#            ResEquip = HistoriqueEquip.objects.filter(qset).distinct()
    else:
        results = []
    return render_to_response("histoequip.html", {
        "ResCatgEquip": ResCatgEquip,
        "ResCons": ResCons,
        "ResFourn": ResFourn,
        "ResEquip": ResEquip,
        "ResEventEquip": ResEventEquip,
        "ResEquipStationSite" : ResEquipStationSite,
        "query": query,
        "query2": query2,
        "queryevent": queryevent,
        "querycat" : querycat,
        "querycons" : querycons,
        "queryfourn" : queryfourn
    })


