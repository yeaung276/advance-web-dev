from django.contrib import admin
from . import models


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "bibcode", "doi", "secondary")
    search_fields = ("name",)
