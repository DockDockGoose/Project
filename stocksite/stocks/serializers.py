from rest_framework import serializers
from djongo import models
from .models import Stock

class StockSerializer(serializers.Serializer):
    stockSymbol = models.CharField(max_length=50)
    price = models.FloatField()
    quoteServerTime = models.IntegerField()
    sharesAmount = models.FloatField()

    class Meta:
        model = Stock
        fields = ('stockSymbol', 'price', 'quoteServerTime', 'sharesAmount')