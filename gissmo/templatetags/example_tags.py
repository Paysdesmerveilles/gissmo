from __future__ import unicode_literals
from django import template
from gissmo.models import *  # NOQA
import operator

from django.contrib.contenttypes.models import ContentType

register = template.Library()


@register.inclusion_tag('channel_comments.html')
def display_channel_comments(channel_id):
    liste = []
    comments = []
    comments = CommentChannel.objects.filter(
        channel__id=channel_id).order_by('-begin_effective')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(CommentChannel)
    url_redirection = "admin:%s_commentchannel_change" % (
        content_type.app_label)
    "Find the authors of the comment"
    if comments:
        for comment in comments:
            authors = CommentChannelAuthor.objects.filter(
                comment_channel__id=comment.id)
            liste_authors = []
            if authors:
                for author in authors:
                    liste_authors.append(author.author.actor_name)
            liste.append([comment, liste_authors])
    return {'comments': liste, 'url_redirection': url_redirection}


@register.inclusion_tag('stationsite_comments.html')
def display_stationsite_comments(station_id):
    liste = []
    comments = []
    comments = CommentStationSite.objects.filter(
        station__id=station_id).order_by('-begin_effective')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(CommentStationSite)
    url_redirection = "admin:%s_commentstationsite_change" % (
        content_type.app_label)
    "Find the authors of the comment"
    if comments:
        for comment in comments:
            authors = CommentStationSiteAuthor.objects.filter(
                comment_station__id=comment.id)
            liste_authors = []
            if authors:
                for author in authors:
                    liste_authors.append(author.author.actor_name)
            liste.append([comment, liste_authors])
    return {'comments': liste, 'url_redirection': url_redirection}


@register.inclusion_tag('network_comments.html')
def display_network_comments(network_id):
    liste = []
    comments = []
    comments = CommentNetwork.objects.filter(
        network__id=network_id).order_by('-begin_effective')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(CommentNetwork)
    url_redirection = "admin:%s_commentnetwork_change" % (
        content_type.app_label)
    "Find the authors of the comment"
    if comments:
        for comment in comments:
            authors = CommentNetworkAuthor.objects.filter(
                comment_network__id=comment.id)
            liste_authors = []
            if authors:
                for author in authors:
                    liste_authors.append(author.author.actor_name)
            liste.append([comment, liste_authors])
    return {'comments': liste, 'url_redirection': url_redirection}


@register.inclusion_tag('station_states.html')
def display_station_states(station_id):
    states = []
    states = IntervStation.objects.filter(
        intervention__station__id=station_id,
        station_state__isnull=False).order_by(
            '-intervention__intervention_date')
    return {'states': states}


@register.inclusion_tag('station_actions.html')
def display_station_actions(station_id):
    actions = []
    actions = IntervStation.objects.filter(
        intervention__station__id=station_id).order_by(
            '-intervention__intervention_date')
    return {'actions': actions}


@register.inclusion_tag('station_interventions.html')
def display_station_interventions(station_id):
    liste = []
    intervs = []
    intervs = Intervention.objects.filter(
        station_id=station_id).order_by('-intervention_date')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Intervention)
    url_redirection = "admin:%s_intervention_change" % (content_type.app_label)

    # TODO: add global function to obtain that information
    last_station_state = IntervStation.objects.filter(
        intervention__station__id=station_id,
        station_state__isnull=False).order_by(
            '-intervention__intervention_date')
    if last_station_state:
        last_state = dict(StationState.STATION_STATES)[
            last_station_state[0].station_state]
    else:
        last_state = 'Inconnu'

    "Find the actors for each station intervention"
    if intervs:
        for interv in intervs:
            intervactors = IntervActor.objects.filter(
                intervention_id=interv.id)
            intervstations = IntervStation.objects.filter(
                intervention_id=interv.id)
            intervequips = IntervEquip.objects.filter(
                intervention_id=interv.id)
            liste_actors = []
            if intervactors:
                for intervactor in intervactors:
                    liste_actors.append(intervactor.actor)
            liste_stations = []
            if intervstations:
                for intervstation in intervstations:
                    liste_stations.append(intervstation)
            liste_equips = []
            if intervequips:
                for intervequip in intervequips:
                    liste_equips.append(intervequip)

            if intervstations.count() + intervequips.count() == 0:
                nbrligne = 1
            else:
                nbrligne = intervstations.count() + intervequips.count()

            liste.append([interv, liste_actors, liste_stations,
                          liste_equips, nbrligne, last_state])
    return {'intervs': liste, 'url_redirection': url_redirection}


@register.inclusion_tag('equip_states.html')
def display_equip_states(equip_id):
    """
    """
    states = []
    states = IntervEquip.objects.filter(
        equip__id=equip_id,
        equip_state__isnull=False).order_by('-intervention__intervention_date')
    return {'states': states}


@register.inclusion_tag('equip_actions.html')
def display_equip_actions(equip_id):
    """
    """
    actions = []
    actions = IntervEquip.objects.filter(equip__id=equip_id).order_by(
        '-intervention__intervention_date')
    return {'actions': actions}


@register.inclusion_tag('equip_interventions.html')
def display_equip_interventions(equip_id):
    intervs = []
    intervs = IntervEquip.objects.filter(equip__id=equip_id).order_by(
        '-intervention__intervention_date')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(IntervEquip)
    url_redirection = "admin:%s_intervention_change" % (content_type.app_label)

    return {'intervs': intervs, 'url_redirection': url_redirection}


@register.inclusion_tag('equip_locations.html')
def display_equip_locations(equip_id):
    """
    """
    locations = []
    locations = IntervEquip.objects.filter(
        equip__id=equip_id,
        station__isnull=False).order_by('-intervention__intervention_date')
    return {'locations': locations}


@register.inclusion_tag('equip_last_locations.html')
def display_equip_last_location(station_id):
    """
    TODO: Obtain the last location of the equipment before link to station
    This solution is not optimal.

    For each equipment we obtain the last location.
    We must validate that this location equal to the station we visualize

    If the result is not empty compare that the last station is the station
    that we visualize.
    """
    liste = []
    equipments = Equipment.objects.all()
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Equipment)
    url_redirection = "admin:%s_equipment_change" % (content_type.app_label)

    for equip in equipments:
        last_equip_location = IntervEquip.objects.filter(
            equip__id=equip.id,
            station__isnull=False).order_by(
                '-intervention__intervention_date')[:1]
        if last_equip_location:
            for last in last_equip_location:
                liste.append(last.id)
    # Changing the order by fr presenting the equipment by
    # supertype, type, model.
    locations = IntervEquip.objects.filter(
        station=station_id,
        id__in=liste).order_by(
            'equip__equip_supertype',
            'equip__equip_type',
            'equip__equip_model')
    return {'locations': locations, 'url_redirection': url_redirection}


@register.inclusion_tag('hist_equip_station.html')
def display_hist_equip_station(station_id):
    """
    Obtain the equipment who was installed on the station.

    TODO: Check that this is the last place or find the end date on the
    next intervention.

    Toutes les interventions pour lesquelles les equipements ont été
    présents pour un moment a la station.

    TODO: Historique of equipment location.
    equip.id station_code built.__unicode__ start_date end_date
    trie en ordre descendent date intervention
    iteration si station <> precedent sauvegarde precedent
                                      end_date == date_precedent
                                      start_date == date_courante

              si station = precedent start_date == date_courante
    end iteration sauvegarde
    """
    locations = IntervEquip.objects.filter(
        station__id=station_id).order_by('-intervention__intervention_date')
    liste = []
    liste_sorted = []
    for location in locations:
        liste.append(location.equip.id)

    # Tous les equipements ayant ete presents a un moment a la station
    equipments = Equipment.objects.filter(id__in=liste)
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Equipment)
    url_redirection = "admin:%s_equipment_change" % (content_type.app_label)

    # Tous les emplacmements des équipements ayant été présents à un moment
    # à la station.
    liste = []
    for equip in equipments:
        last_equip_location = IntervEquip.objects.filter(
            equip__id=equip.id).order_by('-intervention__intervention_date')
        prec = ''
        built_precedente = ''
        start_date_precedente = ''
        end_date_precedente = ''
        etat_precedent = ''
        if not isinstance(station_id, int):
            station_id = int(station_id)
        for location in last_equip_location:
            loc_stat = location.station
            if loc_stat != prec and prec != '':
                # Ne conserver que les emplacements avec une date de fin et
                # pour la station concernee
                if prec.id == station_id and end_date_precedente != '':
                    liste.append([
                        equip,
                        start_date_precedente,
                        end_date_precedente,
                        prec,
                        built_precedente,
                        etat_precedent])
                end_date_precedente = start_date_precedente
                prec = loc_stat
                built_precedente = location.built
                start_date_precedente = location.intervention.intervention_date
            else:
                if prec == '':
                    etat_precedent = location.equip_state
                prec = loc_stat
                built_precedente = location.built
                start_date_precedente = location.intervention.intervention_date
        if prec.id == station_id and end_date_precedente != '':
            liste.append([
                equip,
                start_date_precedente,
                end_date_precedente,
                prec,
                built_precedente,
                etat_precedent])

    # Trie descendant sur date de fin
    liste_sorted = sorted(liste, key=operator.itemgetter(2), reverse=True)
    return {'locations': liste_sorted, 'url_redirection': url_redirection}


@register.inclusion_tag('equip_last_station.html')
def equip_last_station(equip_id):
    liste = []
    last_equip_location = IntervEquip.objects.filter(
        equip=equip_id,
        station__isnull=False).order_by('-intervention__intervention_date')[:1]
    if last_equip_location:
        for last in last_equip_location:
            liste.append(last.station.id)
    else:
        station = StationSite.objects.get(station_code='NEANT')
        liste.append(station.id)
    return {'locations': liste}

#
# Channel link chech it s use
#
#


@register.inclusion_tag('channel_link.html')
def channel_link(intervention_id):
    intervention = Intervention.objects.get(id=intervention_id)
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Intervention)
    url_redirection = "admin:%s_protochannel_add" % (content_type.app_label)
    return {
        'station': intervention.station.id,
        'url_redirection': url_redirection}


@register.inclusion_tag('station_channels.html')
def display_station_channels(station_id):
    liste = []
    channels = []
    channels = Channel.objects.filter(station__id=station_id).order_by(
        '-start_date', 'location_code', '-channel_code')
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Channel)
    url_redirection = "admin:%s_channel_change" % (content_type.app_label)
    "Find the equipments of the acquisition chain"
    if channels:
        for channel in channels:
            chains = Chain.objects.filter(
                channel_id=channel.id).order_by('order')
            liste_equipments = []
            if chains:
                for chain in chains:
                    liste_equipments.append(chain.equip)
            liste.append([channel, liste_equipments])
    return {'channels': liste, 'url_redirection': url_redirection}
