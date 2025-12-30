from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view

from django.db.models import Count, F
from django.shortcuts import get_object_or_404

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from . import models, serializers


class EventPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class EventViewSet(ViewSet):
    pagination_class = EventPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page",
                type=openapi.TYPE_INTEGER,
            ),
        ]
    )
    def list(self, request):
        queryset = models.Event.objects.all()

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        serializer = serializers.EventSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Denormalize the events into the original OSC schema"
    )
    def retrieve(self, request, pk=None):
        event = get_object_or_404(models.Event, pk=pk)
        serializer = serializers.EventDetailSerializer(event)
        return Response(serializer.data)

    # def create(self, request):
    #     serializer = serializers.EventSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
@api_view(["GET"])
def galaxy_by_supernova_count(request):
    rows = (
        models.HostGalaxy.objects
        .select_related("galaxy", "event")
        .values("galaxy__id", "galaxy__name", "event__name")
        .distinct()
    )

    result = {}
    for r in rows:
        g = r["galaxy__name"]
        result.setdefault(g, set()).add(r["event__name"])

    data = [
        {
            "galaxy": g,
            "supernova_events": sorted(list(events)),
        }
        for g, events in result.items()
    ]

    return Response(data)


@api_view(["GET"])
def galaxy_by_supernova_diversity(request):
    rows = (
        models.HostGalaxy.objects
        .select_related("galaxy")
        .values(
            "galaxy__id",
            "galaxy__name",
            "event__claimed_types__sub_type__name",
        )
        .exclude(event__claimed_types__sub_type__isnull=True)
        .distinct()
    )

    result = {}
    for r in rows:
        g = r["galaxy__name"]
        t = r["event__claimed_types__sub_type__name"]
        result.setdefault(g, set()).add(t)

    data = [
        {
            "galaxy": g,
            "supernova_types": sorted(list(types)),
        }
        for g, types in result.items()
    ]

    return Response(data)

@api_view(["GET"])
def supernova_uncertainty(request):
    queryset = (
        models.Event.objects
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
        .order_by("-total_sources")
    )
    
    return Response(queryset)

@api_view(["GET"])
def subtype_with_conflicting_sn(request):
    # find events with multiple subtype claims
    conflicted_events = (
        models.ClaimedType.objects
        .values("event")
        .annotate(subtype_count=Count("sub_type", distinct=True))
        .filter(subtype_count__gt=1)
        .values_list("event", flat=True)
    )

    # count how often each subtype appears in conflicted events
    queryset = (
        models.ClaimedType.objects
        .filter(event__in=conflicted_events)
        .values("sub_type__name")
        .annotate(
            conflicted_event_count=Count("event", distinct=True)
        )
        .order_by("-conflicted_event_count")
    )
    return Response(queryset)