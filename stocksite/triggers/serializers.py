from rest_framework import serializers
from djongo import models
from .models import Trigger

class TrigggerSerializer(serializers.Serializer):
    username = models.CharField(max_length=50)
    kind = models.CharField(max_length=50)
    stockSymbol = models.CharField(max_length=50)
    price = models.FloatField()
    sharesAmount = models.FloatField()

    class Meta:
        model = Trigger
        fields = ('username', 'kind', 'stockSymbol', 'price', 'sharesAmount')