from rest_framework import viewsets
from rest_framework.response import Response

from . import models

class GalaxyViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({'message': 'List all galaxy'})
    
    def create(self, request):
        return Response({'message': 'Create galaxy'})
    
    def retrieve(self, request, pk=None):
        return Response({'message': f'Get galaxy {pk}'})
    
    def update(self, request, pk=None):
        return Response({'message': f'Update galaxy {pk}'})
    
    def destroy(self, request, pk=None):
        return Response({'message': f'Delete galaxy {pk}'})
