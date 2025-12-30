from rest_framework.routers import DefaultRouter

from django.urls import path, include

from .views import EventViewSet, galaxy_by_supernova_diversity, galaxy_by_supernova_count

app_name = "events"

router = DefaultRouter()
router.register(r"", EventViewSet, basename="events")

urlpatterns = [
    *router.urls,
    path("galaxy-sn-diversity", galaxy_by_supernova_diversity, name="supernova_diversity"),
    path("galaxy-sn-count", galaxy_by_supernova_count, name="supernova_count")
]
