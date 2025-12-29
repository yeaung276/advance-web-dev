from rest_framework import viewsets

from . import models, serializers

class GalaxyViewSet(viewsets.ModelViewSet):
    queryset = models.Galaxy.objects.all()
    serializer_class = serializers.GalaxySerializer
