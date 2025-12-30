from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import models, serializers

class SubTypeViewSet(viewsets.ModelViewSet):
    queryset = models.SubType.objects.all()
    serializer_class = serializers.SubTypeSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
