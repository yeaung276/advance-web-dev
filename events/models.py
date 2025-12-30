from django.db import models


# Event represent supernova event
class Event(models.Model):
    name = models.CharField(max_length=125, unique=True)

    def __str__(self):
        return self.name


# Link table between Event and SubType
class ClaimedType(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="claimed_types"
    )
    sub_type = models.ForeignKey("subtypes.SubType", on_delete=models.PROTECT)
    source = models.ForeignKey("sources.Source", on_delete=models.PROTECT)

    class Meta:
        unique_together = ("event", "sub_type", "source")


# Link table between Event and Galaxy
class HostGalaxy(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="host_galaxies"
    )
    galaxy = models.ForeignKey("galaxies.Galaxy", on_delete=models.PROTECT)
    source = models.ForeignKey("sources.Source", on_delete=models.PROTECT)

    class Meta:
        unique_together = ("event", "galaxy", "source")


# Allowed Attributes Name
class AttributeName(models.TextChoices):
    LUMDIST = "lumdist", "Luminosity distance"
    VELOCITY = "velocity", "Recessional velocity"
    REDSHIFT = "redshift", "Redshift"
    MAX_ABS_MAG = "maxabsmag", "Max absolute magnitude"
    MAX_APP_MAG = "maxappmag", "Max apparent magnitude"


# Attribute Table
class Attribute(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(max_length=32, choices=AttributeName.choices)
    source = models.ForeignKey("sources.Source", on_delete=models.PROTECT)
    value = models.FloatField()
    unit = models.CharField(max_length=32)

    class Meta:
        indexes = [
            models.Index(fields=["event", "name"]),
        ]
