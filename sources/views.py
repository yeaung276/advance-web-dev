from rest_framework import viewsets
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .models import *

class SourceViewSet(viewsets.ViewSet):
    @swagger_auto_schema(operation_description="get all sources")
    def list(self, request):
        return Response({'message': 'List all sources'})
    
    def create(self, request):
        return Response({'message': 'Create source'})
    
    def retrieve(self, request, pk=None):
        return Response({'message': f'Get source {pk}'})
    
    def update(self, request, pk=None):
        return Response({'message': f'Update source {pk}'})
    
    def destroy(self, request, pk=None):
        return Response({'message': f'Delete source {pk}'})