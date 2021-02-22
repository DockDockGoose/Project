from rest_framework import serializers
from .models import Account
from stocks.serializers import SharesSerializer

class AccountSerializer(serializers.ModelSerializer):
    shares = SharesSerializer(many=True)

    class Meta:
        model = Account
        fields = ('username', 'funds', 'pendingFunds', 'shares')
