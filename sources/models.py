from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.CharField(max_length=512, null=True, blank=True)
    bibcode = models.CharField(max_length=19, null=True, blank=True)
    doi = models.CharField(max_length=256, null=True, blank=True)
    secondary = models.BooleanField(default=False, blank=True)
    
    def __str__(self):
        return f"Source: {self.name}"
