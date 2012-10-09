from django import template
from bdmateriel.models import *

register = template.Library()

@register.inclusion_tag('station_states.html')
def display_station_states(station_id):
#    station = models.StationSite.objects.get(id__exact=station_id)
#    states = models.HistoricStationState.objects.select_related(depth=1).filter(station=station).order_by('-start_date')
    states = []
    states = IntervStation.objects.filter(intervention__station__id=station_id,station_state__isnull=False).order_by('-intervention__intervention_date')
    return { 'states': states}

@register.inclusion_tag('station_actions.html')
def display_station_actions(station_id):
#    station = models.StationSite.objects.get(id__exact=station_id)
#    actions = models.HistoricStationAction.objects.select_related(depth=1).filter(station=station).order_by('-start_date')
    actions = []
    actions = IntervStation.objects.filter(intervention__station__id=station_id).order_by('-intervention__intervention_date')
    return { 'actions': actions }

@register.inclusion_tag('station_interventions.html')
def display_station_interventions(station_id):
    intervs = []
    intervs = IntervStation.objects.filter(intervention__station__id=station_id).order_by('-intervention__intervention_date')
    return { 'intervs': intervs}

@register.inclusion_tag('equip_states.html')
def display_equip_states(equip_id):
    """
    """
    states = []
    states = IntervEquip.objects.filter(equip__id=equip_id,equip_state__isnull=False).order_by('-intervention__intervention_date')
    return { 'states': states }

@register.inclusion_tag('equip_actions.html')
def display_equip_actions(equip_id):
    """
    """
    actions = []
    actions = IntervEquip.objects.filter(equip__id=equip_id).order_by('-intervention__intervention_date')
    return { 'actions': actions }

@register.inclusion_tag('equip_interventions.html')
def display_equip_interventions(equip_id):
    intervs = []
    intervs = IntervEquip.objects.filter(equip__id=equip_id).order_by('-intervention__intervention_date')
    return { 'intervs': intervs}

@register.inclusion_tag('equip_locations.html')
def display_equip_locations(equip_id):
    """
    """
    locations = []
    locations = IntervEquip.objects.filter(equip__id=equip_id, station__isnull=False).order_by('-intervention__intervention_date')
    return { 'locations': locations }

@register.inclusion_tag('equip_last_locations.html')
def display_equip_last_location(station_id):
    """
    TODO Obtain the last location of the equipment before link to station
    This solution is not optimal 
    
    For each equipment we obtain the last location
    We must validate that this location equal to the station we visualize
    
    If the result is not empty compare that the last station is the station that we visualize
    """       
    liste = []
    equipments = Equipment.objects.all()
    for equip in equipments:
        last_equip_location = IntervEquip.objects.filter(equip__id=equip.id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
        if last_equip_location:
            for last in last_equip_location:
                liste.append(last.id)
    locations = IntervEquip.objects.filter(station=station_id,id__in=liste).order_by('-intervention__intervention_date')
    return { 'locations': locations }

@register.inclusion_tag('hist_equip_station.html')
def display_hist_equip_station(station_id):
    """
    Obtain the equipment who was installed on the station

    TODO Check that this is the last place or find the end date on the next intervention 
    """       
    """ Toutes les interventions pour lesquelles les equipements ont ete presents pour un moment a la station """

    """
    TODO Historique of equipment location
    equip.id station_code built.__unicode__ start_date end_date 
    trie en ordre descendent date intervention
    iteration si station <> precedent sauvegarde precedent
                                      end_date == date_precedent
                                      start_date == date_courante
                                        
              si station = precedent start_date == date_courante
    end iteration sauvegarde
    """

    locations = IntervEquip.objects.filter(station__id=station_id).order_by('-intervention__intervention_date')
    liste = []
    for location in locations:
        liste.append(location.equip.id)

    """ Tous les equipements ayant ete presents a un moment a la station """
    equipments = Equipment.objects.filter(id__in=liste)

    """ Tous les emplacmements des equipements ayant ete presents a un moment a la station """
    liste = []
    for equip in equipments:
        last_equip_location = IntervEquip.objects.filter(equip__id=equip.id).order_by('-intervention__intervention_date')
        station_precedente = ''
        built_precedente = ''
        start_date_precedente = ''
        end_date_precedente = ''
        etat_precedent = ''
        for location in last_equip_location:
            if location.station != station_precedente and station_precedente != '':
               """ Ne conserver que les emplacements avec une date de fin et pour la station concernee """
               if station_precedente.id == int(station_id) and end_date_precedente != '':
                   liste.append([equip, start_date_precedente, end_date_precedente, station_precedente, built_precedente, etat_precedent])
               end_date_precedente = start_date_precedente
               station_precedente = location.station
               built_precedente = location.built
               start_date_precedente = location.intervention.intervention_date
            else:
               if station_precedente == '':
                   etat_precedent = location.equip_state
               station_precedente = location.station
               built_precedente = location.built
               start_date_precedente = location.intervention.intervention_date
        if station_precedente.id == int(station_id) and end_date_precedente != '':
            liste.append([equip, start_date_precedente, end_date_precedente, station_precedente, built_precedente, etat_precedent])

#    for equip in locations:
#        equipments = Equipment.objects.filter(id__in=Liste)
#        liste.append()
    
#    liste = []
#    print station_id
#    """ Toutes les interventions des equipements """
#    for equip in locations:
#        list_interv_equip = IntervEquip.objects.filter(equip__id=equip.equip.id).order_by('-intervention__intervention_date')
#        denombre = 0
#        for interv_equip in list_interv_equip:
#            liste.append(interv_equip)
#            denombre += 1
#            possible_end_date = interv_equip.intervention.intervention_date
#            station =interv_equip.station.id
#            print possible_end_date
#            print station
#            if interv_equip == equip:
#                if denombre != 1:
#                    if station != equip.station.id:
#                        liste.append(interv_equip.id) 
    return { 'locations': liste }



@register.inclusion_tag('equip_last_station.html')
def equip_last_station(equip_id):
    """
    """
    Liste = []
    last_equip_location = IntervEquip.objects.filter(equip=equip_id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_location:
        for last in last_equip_location:
            Liste.append(last.station.id)
    else:
        station = StationSite.objects.get(station_code='NEANT')
        Liste.append(station.id)
    return { 'locations': Liste }

@register.inclusion_tag('channel_link.html')
def channel_link(intervention_id):
    """
    """
    Liste = []
    intervention = Intervention.objects.get(id=intervention_id)
    return { 'station': intervention.station.id }

@register.inclusion_tag('station_channels.html')
def display_station_channels(station_id):
    channels = []
    channels = Channel.objects.filter(station__id=station_id).order_by('-start_date')
    return { 'channels': channels }

