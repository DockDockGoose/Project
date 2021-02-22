from rest_framework import serializers
from djongo import models
from .models import Shares, Stock

# class StockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Stock
#         fields = ('stockSymbol', 'price', 'quoteServerTime')

class SharesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shares
        fields = ('sharesAmount', 'stocks')