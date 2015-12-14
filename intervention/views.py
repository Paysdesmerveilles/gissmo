from django.shortcuts import (
    get_object_or_404,
    HttpResponse,
    render)
from django.http import JsonResponse

from place.models import Site
from place.transitions import TRANSITION_CHOICES as pchoices


def json_transitions(transitions):
    result = {}
    for choice in pchoices:
        if choice[0] in transitions:
            result[choice[0]] = choice[1]
    return result


def lookup_transitions(request):
    """
    Get given site state allowed transition
    """
    if request.is_ajax() and request.method == 'GET':
        site_number = request.GET.get('site', '')
        if site_number ==  '' or site_number == '0':
            transitions = json_transitions([p[0] for p in pchoices])
            return JsonResponse({'allowed_transitions': transitions})
        site = get_object_or_404(Site, pk=site_number)
        transitions = json_transitions(site.state.allowed_transitions())
        return JsonResponse({'allowed_transitions': transitions})
    return HttpResponse(status=400)
