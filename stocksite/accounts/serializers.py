from rest_framework import serializers
from .models import Account
from djongo import models
from stocks.serializers import StockSerializer

class AccountSerializer(serializers.ModelSerializer):
    stocks = StockSerializer()

    class Meta:
        model = Account
        fields = ('username', 'funds', 'pendingFunds', 'stocks')
