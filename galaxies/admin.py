from django.contrib import admin
from . import models

class GalaxyAdmin(admin.ModelAdmin):
    list_display = ("name", "hostra", "hostdec")
    
admin.site.register(models.Galaxy, GalaxyAdmin)
    
