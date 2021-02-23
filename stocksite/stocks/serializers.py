from rest_framework import serializers
from djongo import models
from .models import Stock

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ('stockSymbol', 'price', 'quoteServerTime', 'sharesAmount')