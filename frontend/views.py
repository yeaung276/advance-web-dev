from django.shortcuts import render
from django.db.models import Count, F

from events.models import Event, HostGalaxy, ClaimedType
from events.serializers import EventDetailSerializer


def home(request):
    return render(request, "home.html")


def search_event(request):
    name = request.GET.get("name")
    event_json = None
    error = None

    if name:
        try:
            event = Event.objects.get(name=name)
            serializer = EventDetailSerializer(event)
            event_json = serializer.data
        except Event.DoesNotExist:
            error = f'Event with name "{name}" not found.'

    context = {
        "query_name": name or "",
        "event_json": event_json,
        "error": error,
    }

    return render(request, "events/search.html", context)


def create_event(request):
    return render(request, "events/create.html", {})


def galaxy_sn_count(request):
    top_n = 5

    queryset = (
        HostGalaxy.objects.values("galaxy__id", "galaxy__name")
        .annotate(supernova_count=Count("event", distinct=True))
        .order_by("-supernova_count")[:top_n]
    )

    context = {
        "results": list(queryset),
        "metric_key": "supernova_count",
        "label_key": "galaxy__name",
        "label": "Supernova Count",
        "title": "Top Galaxies by Supernova Count",
        "api_url_name": "events:supernova_count"
    }
    return render(request, "graphs/sn_bar_chart.html", context)


def galaxy_sn_diversity(request):
    top_n = 5

    queryset = (
        HostGalaxy.objects.values("galaxy__id", "galaxy__name")
        .annotate(
            supernova_type_count=Count("event__claimed_types__sub_type", distinct=True)
        )
        .order_by("-supernova_type_count")[:top_n]
    )

    context = {
        "results": list(queryset),
        "metric_key": "supernova_type_count",
        "label_key": "galaxy__name",
        "label": "Unique SubType count",
        "title": "Top Galaxies by Supernova Type Diversity",
        "api_url_name": "events:supernova_diversity"
    }

    return render(request, "graphs/sn_bar_chart.html", context)

def event_sn_uncertainty(request):
    top_n = int(request.GET.get("limit", 5))

    queryset = (
        Event.objects
        .values("name")
        .annotate(
            subtype_sources=Count("claimed_types__source", distinct=True),
            host_sources=Count("host_galaxies__source", distinct=True),
        )
        .annotate(
            total_sources=(
                F("subtype_sources") +
                F("host_sources") 
            )
        )
        .order_by("-total_sources")[:top_n]
    )

    return render(
        request,
        "graphs/sn_bar_chart.html",
        {
            "results": list(queryset),
            "metric_key": "total_sources",
            "label_key": "name",
            "label": "Conflicting source count",
            "title": "Supernova Events with Highest Data Disagreement",
            "api_url_name": "events:supernova_uncertainty"
        },
    )
    
def subtype_sn_uncertainty(request):
    top_n = int(request.GET.get("limit", 5))

    # find events with multiple subtype claims
    conflicted_events = (
        ClaimedType.objects
        .values("event")
        .annotate(subtype_count=Count("sub_type", distinct=True))
        .filter(subtype_count__gt=1)
        .values_list("event", flat=True)
    )

    # count how often each subtype appears in conflicted events
    queryset = (
        ClaimedType.objects
        .filter(event__in=conflicted_events)
        .values("sub_type__name")
        .annotate(
            conflicted_event_count=Count("event", distinct=True)
        )
        .order_by("-conflicted_event_count")[:top_n]
    )

    return render(
        request,
        "graphs/sn_bar_chart.html",
        {
            "results": list(queryset),
            "metric_key": "conflicted_event_count",
            "label_key": "sub_type__name",
            "label": "Conflicting supernova count",
            "title": "Supernova SubType with Conflicting Classifications",
            "api_url_name": "events:subtype_uncertainty"
        },
    )