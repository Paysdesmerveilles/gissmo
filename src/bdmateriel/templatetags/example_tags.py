from django import template
from bdmateriel.models import *

register = template.Library()

@register.inclusion_tag('station_states.html')
def display_station_states(station_id):
#    station = models.StationSite.objects.get(id__exact=station_id)
#    states = models.HistoricStationState.objects.select_related(depth=1).filter(station=station).order_by('-start_date')
    states = []
    test = IntervStation.objects.filter(intervention__station__id=station_id)
    print test
    states = IntervStation.objects.filter(intervention__station__id=station_id,station_state__isnull=False).order_by('-intervention__intervention_date')
    print states
    return { 'states': states}

@register.inclusion_tag('station_actions.html')
def display_station_actions(station_id):
#    station = models.StationSite.objects.get(id__exact=station_id)
#    actions = models.HistoricStationAction.objects.select_related(depth=1).filter(station=station).order_by('-start_date')
    actions = []
    actions = IntervStation.objects.filter(intervention__station__id=station_id).order_by('-intervention__intervention_date')
    return { 'actions': actions }

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
    Liste = []
    equipments = Equipment.objects.all()
    for equip in equipments:
        last_equip_location = IntervEquip.objects.filter(equip__id=equip.id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
        if last_equip_location:
            for last in last_equip_location:
                Liste.append(last.id)
    locations = IntervEquip.objects.filter(station=station_id,id__in=Liste).order_by('-intervention__intervention_date')
    return { 'locations': locations }

@register.inclusion_tag('equip_last_station.html')
def equip_last_station(equip_id):
    """
    """
    Liste = []
    last_equip_location = IntervEquip.objects.filter(equip=equip_id, station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_location:
        for last in last_equip_location:
            Liste.append(last.station.id)
    return { 'locations': Liste }
    return

