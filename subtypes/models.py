from django.db import models

class SubType(models.Model):
    name = models.CharField(max_length=126, null=False, blank=False)
    
    def __str__(self):
        return f"SubType: {self.name}"
