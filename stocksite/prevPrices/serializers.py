from rest_framework import serializers
from djongo import models
from .models import PrevPrices

class PrevPricesSerializer(serializers.ModelSerializer):
    """
    Serializer used for front end stock representations (primary key relationship).
    """
    class Meta:
        model = PrevPrices
        fields = '__all__'
