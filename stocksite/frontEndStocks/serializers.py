from rest_framework import serializers
from djongo import models
from .models import FrontEndStock

class FrontEndStockSerializer(serializers.ModelSerializer):
    """
    Serializer used for front end stock representations (primary key relationship).
    """
    class Meta:
        model = FrontEndStock
        fields = '__all__'
