from django.db import models

class Galaxy(models.Model):
    name = models.CharField(max_length=256, null=False, blank=False, db_index=True)
    
    def __str__(self):
        return f"Galaxy: {self.name}"