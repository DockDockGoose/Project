from rest_framework import serializers
from .models import Account
from stocks.serializers import StockSerializer

class AccountSerializer(serializers.ModelSerializer):
    stocks = StockSerializer(many=True)

    class Meta:
        model = Account
        fields = ('username', 'funds', 'pendingFunds', 'stocks')
