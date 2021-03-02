from django.test import TestCase
from ..models import Transaction
from .factories import TransactionFactory

class TransactionsTestCase(TestCase):
    def test_str(self):
        """Test for string representation."""
        transaction = TransactionFactory()
        self.assertEqual(str(transaction), transaction.name)