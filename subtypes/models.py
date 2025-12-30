from django.db import models


class SubType(models.Model):
    name = models.CharField(max_length=126, null=False, blank=False, db_index=True)

    def __str__(self):
        return f"SubType: {self.name}"
