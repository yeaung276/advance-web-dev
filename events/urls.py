from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .views import (
    EventViewSet,
    galaxy_by_supernova_diversity,
    galaxy_by_supernova_count,
    subtype_with_conflicting_sn,
    supernova_uncertainty,
)

app_name = "events"

router = DefaultRouter()
router.register(r"", EventViewSet, basename="events")

urlpatterns = [
    *router.urls,
    path(
        "galaxy-sn-diversity", galaxy_by_supernova_diversity, name="supernova_diversity"
    ),
    path("galaxy-sn-count", galaxy_by_supernova_count, name="supernova_count"),
    path("supernova-uncertainty", supernova_uncertainty, name="supernova_uncertainty"),
    path("subtype-uncertainty", subtype_with_conflicting_sn, name="subtype_uncertainty"),
]
