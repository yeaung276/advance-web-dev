from django.urls import path
from .views import (
    home,
    search_event,
    create_event,
    galaxy_sn_count,
    galaxy_sn_diversity,
)

app_name = "frontend"

urlpatterns = [
    path("", home, name="home"),
    path("events/search", search_event, name="search_event"),
    path("events/create", create_event, name="create_event"),
    path("graphs/galaxy-sn-count", galaxy_sn_count, name="galaxy_sn_count"),
    path("graphs/galaxy-sn-diversity", galaxy_sn_diversity, name="galaxy_sn_diversity"),
]
