# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from gissmo.models import *  # NOQA

import operator

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
    """
    Fetch all site interventions.
    For each intervention on this site gives this informations:
      - involved actors
      - involved equipments
    """
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Intervention)
    url_redirection = "admin:%s_intervention_change" % (content_type.app_label)

    # Station state
    last_state = _('Unknown')
    i = IntervStation.objects.filter(
        intervention__station__id=station_id,
        station_state__isnull=False).order_by(
            '-intervention__intervention_date').first()
    if i:
        last_state = StationState.STATION_STATES[i.station_state][1]

    # Fetch all interventions on the given site (and all related data)
    liste = []
    interventions = Intervention.objects.filter(
        station_id=station_id).order_by(
        '-intervention_date').prefetch_related(
        'intervactor_set__actor',
        'intervequip_set__equip__equip_model',
        'intervequip_set__built',
        'intervstation_set')
    for intervention in interventions:
        actors = [a.actor for a in intervention.intervactor_set.all()]
        stations = [ivs for ivs in intervention.intervstation_set.all()]
        equips = [ie for ie in intervention.intervequip_set.all()]

        if not stations and not equips:
            line_number = 1
        else:
            line_number = len(stations) + len(equips)

        liste.append([intervention, actors, stations,
                      equips, line_number, last_state])
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
    Main idea is to gives current Equipment on this station.
    As Equipment are linked to Station with IntervEquip, we must search as:
      - all equipment linked to this station (even in the past)
      - for each equipment use its last intervention (even if it's in another
station)
      - filtering the result with only given station
    """
    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Equipment)
    url_redirection = "admin:%s_equipment_change" % (content_type.app_label)

    liste = []
    # First we limit request to the given station
    station_equipments = IntervEquip.objects.filter(
        station_id=station_id)
    station_equipments.query.group_by = ['equip']
    # Then we will only take last intervention of each equipment
    e_ids = [i.equip_id for i in station_equipments]
    e_ids = set(e_ids)  # delete doublons
    # station_id__isnull is important because it permit to take last
    # intervention of each equipment that WAS in the given station.
    # After that, we make a new query on intervention to limit equipment
    # that is in the given station yet.
    for e_id in e_ids:
        i = IntervEquip.objects.filter(
            equip_id=e_id,
            station_id__isnull=False).order_by(
                'intervention__intervention_date').last()
        if i:
            liste.append(i.id)
    # Finally we sort result by supertype, type and model
    locations = IntervEquip.objects.filter(
        station_id=station_id,
        id__in=liste).order_by(
            'equip__equip_model__equip_type__equip_supertype',
            'equip__equip_model__equip_type',
            'equip__equip_model',
            '-intervention__intervention_date').prefetch_related(
            'intervention',
            'built',
            'equip')

    return {'locations': locations, 'url_redirection': url_redirection}


def intervention_history_element_process(element):
    """
    Exclude given elements:
      - start_date = end_date
      - start_date is None
      - end_date is None
    """
    if element is not None:
        start = element[1]
        end = element[2]
        if start == end or start is None or end is None:
            return None
    return element


def intervention_history_process(last, current, start, station_id):
    """
    Process interventions (last one and current one) to detect some cases:
      - equipement change
      - station change
      - built change
    If any change, we need to set an element to be included in the history.
    Element is composed of:
      - Equipment object
      - First date of intervention that add the Equipment in the station
      - Last date of intervention in which we change this equipment from
given station of last built
      - The built from this station in which the equipment was


    Return an history_element (or None) and the updated start date:
      - if station change, start date is None
      - otherwise start date is current intervention date
    """
    element = None
    current_date = current.intervention.intervention_date
    # first intervention have no previous one.
    if last is None:
        start = current_date
        return element, start
    # Cases where to create an new element
    if current.equip_id != last.equip_id:
        end_date = last.intervention.intervention_date
        element = [
            last.equip,
            start,
            end_date,
            last.built]
        start = current_date
    elif current.station_id != last.station_id:
        # Equipment left out the current station (last station was the current
        # one)
        if last.station_id == station_id:
            end_date = current_date
            element = [
                current.equip,
                start or last.intervention.intervention_date,
                end_date,
                last.built]
            start = None
        # Equipment join the current station
        elif current.station_id == station_id:
            start = current_date
        # Equipment was in another station than the current one AND
        # is now in another one that is not the current one.
        else:
            start = None
    elif current.built_id != last.built_id and last.station_id == station_id:
        end_date = current_date
        element = [
            current.equip,
            start,
            end_date,
            last.built]
        start = current_date

    # Exclude some elements
    element = intervention_history_element_process(element)
    return element, start


@register.inclusion_tag('hist_equip_station.html')
def display_hist_equip_station(station_id):
    """
    Equipment history of the given site (station_id).

    An history line is a period in which the equipment was on the given site.

    The start date begins when the equipment was attached to the given site.
    The end date is when the equipment:
      - change its built (in the same site)
      - change its site

    If the equipment is currently present on the site we don't show its last
    date in which it joins the site.

    We sort list with end_date to have last one at the beginning.
    """
    # WARNING: station_id is a string. Must be an integer to do comparisons.
    if not isinstance(station_id, int):
        station_id = int(station_id)

    # Obtain the app_label
    content_type = ContentType.objects.get_for_model(Equipment)
    url_redirection = "admin:%s_equipment_change" % (content_type.app_label)

    # First we search all equipments linked to this station
    intervequip = IntervEquip.objects.filter(
        station__id=station_id)
    intervequip.query.group_by = ['equip_id']
    equipment_ids = [i.equip_id for i in intervequip]
    interventions = IntervEquip.objects.filter(
        equip_id__in=equipment_ids).order_by(
        'equip',
        'intervention__intervention_date').prefetch_related(
        'built',
        'station',
        'intervention',
        'equip__equip_model__equip_type__equip_supertype')

    # Then we browse interventions (ordered by equip) to fetch info
    history = []
    last_intervention = None
    start_date = None

    for current_intervention in interventions:
        history_element, start_date = intervention_history_process(
            last_intervention,
            current_intervention,
            start_date,
            station_id)
        if history_element is not None:
            history.append(history_element)
        last_intervention = current_intervention

    # Finally sort history by end_date
    liste_sorted = sorted(history, key=operator.itemgetter(2), reverse=True)
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
