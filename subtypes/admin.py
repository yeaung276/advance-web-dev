from django.contrib import admin

from . import models

@admin.register(models.SubType)
class SubTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    
