from rest_framework import serializers
from .models import Transaction

"""
more customization can be added, such as:

outputting fields that don’t exist on the model (maybe something like is_new_company, or other data that can be calculated on the backend)
custom validation logic for when data is sent to the endpoint for any of the fields
custom logic for creates (POST requests) or updates (PUT or PATCH requests)
"""

# Serializers define the API representation.
class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer used for transaction data representations (primary key relationship).
    Can also use HyperlinkedModelSerializer for hyperlinked relations.
    """
    class Meta:
        model = Transaction
        fields = '__all__'
