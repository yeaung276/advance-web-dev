from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False)
    url = models.CharField(max_length=512, null=True, blank=True)
    bibcode = models.CharField(max_length=19, null=True, blank=True)
    doi = models.CharField(max_length=256, null=True, blank=True)
    secondary = models.BooleanField(default=False, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["url"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["bibcode"],
                condition=models.Q(bibcode__isnull=False),
                name="unique_bibcode_when_not_null",
            ),
            models.UniqueConstraint(
                fields=["doi"],
                condition=models.Q(doi__isnull=False),
                name="unique_doi_when_not_null",
            ),
        ]

    def __str__(self):
        return f"Source: {self.name}"
