from rest_framework import viewsets

from . import models, serializers

class SubTypeViewSet(viewsets.ModelViewSet):
    queryset = models.SubType.objects.all()
    serializer_class = serializers.SubTypeSerializer
