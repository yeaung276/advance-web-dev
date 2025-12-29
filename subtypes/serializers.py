from rest_framework import serializers
from .models import SubType

class SubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubType
        fields = ["id", "name"]