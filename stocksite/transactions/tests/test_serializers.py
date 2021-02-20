from django.test import TestCase
from ..serializers import TransactionSerializer
from .factories import TransactionFactory

class TransactionSerializer(TestCase):
    def test_model_fields(self):
        """Serializer data matches the Transaction object for each field."""
        transaction = TransactionFactory()
        for field_name in ['type', 'timestamp', 'server', 'transactionNum', 
            'command', 'username', 'stockSymbol', 'amount']:
            self.assertEqual(serializer.data[field_name], getattr(transaction, field_name))