from rest_framework import serializers
from .models import Transactions

class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer used for transaction data representations. Of type HyperlinkedModelSerializer so we can
    use hyperlinked relations. Can also use other Serializers such as for primary key relationships.
    """
    class Meta:
        model = Transactions
        fields = '__all__'
