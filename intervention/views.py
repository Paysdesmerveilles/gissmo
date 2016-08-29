from django.shortcuts import HttpResponse
from django.http import JsonResponse

# from equipment.transitions import TRANSITION_CHOICES as pchoices


def json_transitions(transitions):
    result = {}
#    for choice in pchoices:
#        if choice[0] in transitions:
#            result[choice[0]] = choice[1]
    return result


def lookup_transitions(request):
    """
    Get given station state allowed transition
    """
    if request.is_ajax() and request.method == 'GET':
        transitions = {}
#        station_number = request.GET.get('station', '')
#        if station_number == '' or station_number == '0':
#            transitions = json_transitions([p[0] for p in pchoices])
#            return JsonResponse({'allowed_transitions': transitions})
#        station = get_object_or_404(Place, pk=station_number)
#        transitions = json_transitions(station.state.allowed_transitions())
        return JsonResponse({'allowed_transitions': transitions})
    return HttpResponse(status=400)
