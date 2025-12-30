from django.contrib import admin
from . import models


@admin.register(models.Galaxy)
class GalaxyAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
