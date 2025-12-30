from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import models, serializers

class GalaxyViewSet(viewsets.ModelViewSet):
    queryset = models.Galaxy.objects.all()
    serializer_class = serializers.GalaxySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
