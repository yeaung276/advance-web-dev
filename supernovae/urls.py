"""
URL configuration for supernovae project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from drf_yasg import openapi
from drf_yasg.views import get_schema_view as get_swagger_schema_view

schema_view = get_swagger_schema_view(
    openapi.Info(
        title="Supernovae API",
        default_version="1.0.0",
        description="API documentation for supernovae record"
    ),
    public=True,
)

urlpatterns = [
    path('', include("frontend.urls"), name="frontend"),
    path('admin/', admin.site.urls, name="admin"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=10), name="docs"),
    path('api/', 
        include([
            path("sources/", include("sources.urls"), name="source"),
            path("galaxies/", include("galaxies.urls"), name="galaxy"),
            path("subtypes/", include("subtypes.urls"), name="subtype"),
        ])
    ),
]
