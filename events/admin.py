from django.contrib import admin

from . import models


class ClaimedTypeInline(admin.TabularInline):
    model = models.ClaimedType
    extra = 0
    autocomplete_fields = ["sub_type", "source"]


class AttributeInline(admin.TabularInline):
    model = models.Attribute
    extra = 0
    autocomplete_fields = ["source"]
    fields = ("name", "value", "unit", "source")


class HostGalaxyInline(admin.TabularInline):
    model = models.HostGalaxy
    extra = 0
    autocomplete_fields = ["galaxy", "source"]
    fields = ("galaxy", "source")


@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

    inlines = [ClaimedTypeInline, AttributeInline, HostGalaxyInline]
