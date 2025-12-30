from django.shortcuts import render
from django.db.models import Count

from events.models import Event, HostGalaxy
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

    print(list(queryset))

    context = {
        "results": list(queryset),
        "metric": "supernova_count",
        "title": "Top Galaxies by Supernova Count",
        "api_url_name": "events:supernova_count"
    }
    return render(request, "graphs/galaxy_sn_chart.html", context)


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
        "metric": "supernova_type_count",
        "title": "Top Galaxies by Supernova Type Diversity",
        "api_url_name": "events:supernova_diversity"
    }

    return render(request, "graphs/galaxy_sn_chart.html", context)
