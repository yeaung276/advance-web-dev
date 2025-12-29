from rest_framework import viewsets
from rest_framework.response import Response

from . import models

class SubTypeViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({'message': 'List all subtype'})
    
    def create(self, request):
        return Response({'message': 'Create subtype'})
    
    def retrieve(self, request, pk=None):
        return Response({'message': f'Get subtype {pk}'})
    
    def update(self, request, pk=None):
        return Response({'message': f'Update subtype {pk}'})
    
    def destroy(self, request, pk=None):
        return Response({'message': f'Delete subtype {pk}'})
