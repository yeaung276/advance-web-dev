from django.contrib import admin

from . import models

class SubTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    
    
admin.site.register(models.SubType, SubTypeAdmin)
