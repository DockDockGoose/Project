from rest_framework import serializers
from djongo import models
from .models import Trigger

class TriggerSerializer(serializers.Serializer):
    username = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    stockSymbol = models.CharField(max_length=50)
    price = models.FloatField()
    sharesAmount = models.FloatField()

    class Meta:
        model = Trigger
        fields = ('username', 'type', 'stockSymbol', 'price', 'sharesAmount')