from django.contrib import admin
from . import models

class SourceAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "bibcode", "doi", "secondary")
    
admin.site.register(models.Source, SourceAdmin)
