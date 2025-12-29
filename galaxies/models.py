from django.db import models

class Galaxy(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)

    hostra = models.TimeField(null=True, blank=True)	# Right ascension of the host galaxy in hours (hh:mm:ss)
    hostdec = models.FloatField(null=True, blank=True)	# Declination of the host galaxy in degrees
    
    def __str__(self):
        return f"Galaxy: {self.name}"