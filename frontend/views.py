from django.shortcuts import render, redirect
from django.db.models import Count, F
from django.http import HttpResponseBadRequest

from events.models import Event, HostGalaxy, ClaimedType
from events.serializers import EventOSCSchemaSerializer
from frontend.forms import (
    EventForm,
    AttributeFormSet,
    ClaimedTypeFormSet,
    HostGalaxyFormSet,
)


def home(request):
    return render(request, "home.html")


# ===================== Search Event Views ==================
def search_event(request):
    name = request.GET.get("name")
    event_json = None
    error = None

    if name:
        try:
            event = Event.objects.get(name=name)
            serializer = EventOSCSchemaSerializer(event)
            event_json = serializer.data
        except Event.DoesNotExist:
            error = f'Event with name "{name}" not found.'

    context = {
        "query_name": name or "",
        "event_json": event_json,
        "error": error,
    }

    return render(request, "events/search.html", context)


# ================== Create Event Views ======================
def create_event(request):
    if request.method == "POST":
        event_form = EventForm(request.POST)
        attr_formset = AttributeFormSet(request.POST)
        claimed_type_formset = ClaimedTypeFormSet(request.POST)
        host_galaxy_formset = HostGalaxyFormSet(request.POST)

        if (
            event_form.is_valid()
            and attr_formset.is_valid()
            and claimed_type_formset.is_valid()
            and host_galaxy_formset.is_valid()
        ):
            event = event_form.save()
            attr_formset.instance = event
            attr_formset.save()
            claimed_type_formset.instance = event
            claimed_type_formset.save()
            host_galaxy_formset.instance = event
            host_galaxy_formset.save()
            
            return redirect("frontend:create_event")
    else:
        event_form = EventForm()
        attr_formset = AttributeFormSet()
        claimed_type_formset = ClaimedTypeFormSet()
        host_galaxy_formset = HostGalaxyFormSet()

    return render(
        request,
        "events/create.html",
        {
            "event_form": event_form,
            "attr_formset": attr_formset,
            "claimed_type_formset": claimed_type_formset,
            "host_galaxy_formset": host_galaxy_formset,
        },
    )

FORMSET_MAP = {
    "attr": (AttributeFormSet, "events/partials/attribute.html"),
    "claimed-types": (ClaimedTypeFormSet, "events/partials/claimed-types.html"),
    "host-galaxy": (HostGalaxyFormSet, "events/partials/host-galaxy.html"),
}

def htmlx_formset_row(request, kind):
    if kind not in FORMSET_MAP:
        return HttpResponseBadRequest("Invalid formset")

    index = int(request.GET["index"])
    formset_class, template_name = FORMSET_MAP[kind]

    formset = formset_class(prefix=kind)
    form = formset.empty_form
    form.prefix = f"{kind}-{index}"

    return render(
        request,
        template_name,
        {"form": form},
    )


# ============= Statistical Views ==================
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
        "api_url_name": "events:supernova_count",
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
        "api_url_name": "events:supernova_diversity",
    }

    return render(request, "graphs/sn_bar_chart.html", context)


def event_sn_uncertainty(request):
    top_n = int(request.GET.get("limit", 5))

    queryset = (
        Event.objects.values("name")
        .annotate(
            subtype_sources=Count("claimed_types__source", distinct=True),
            host_sources=Count("host_galaxies__source", distinct=True),
        )
        .annotate(total_sources=(F("subtype_sources") + F("host_sources")))
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
            "api_url_name": "events:supernova_uncertainty",
        },
    )


def subtype_sn_uncertainty(request):
    top_n = int(request.GET.get("limit", 5))

    # find events with multiple subtype claims
    conflicted_events = (
        ClaimedType.objects.values("event")
        .annotate(subtype_count=Count("sub_type", distinct=True))
        .filter(subtype_count__gt=1)
        .values_list("event", flat=True)
    )

    # count how often each subtype appears in conflicted events
    queryset = (
        ClaimedType.objects.filter(event__in=conflicted_events)
        .values("sub_type__name")
        .annotate(conflicted_event_count=Count("event", distinct=True))
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
            "api_url_name": "events:subtype_uncertainty",
        },
    )
