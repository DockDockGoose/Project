from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .utils import getByStockSymbol
from time import time


class CommitSellView(APIView):
    """
    API endpoint for confirming the sell of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        # Test values (uncomment to populate the db)
        # stockSymbol = 'NISSAN'
        # amount = 300.00
        
        # Check cache for recent sell transaction (within 60 sec), if non-existent log errorEvent
        # stockSymbol = fromcache
        # amount = fromcache

        # Find user account
        account = Account.objects.filter(username=username).first()

        # Search account for stock
        stock = getByStockSymbol(account.stocks, stockSymbol)

        # Subtract amount from stock sharesAmount & add amount to account funds
        stock['sharesAmount'] -= amount
        account.funds += amount
        account.save()

        # Log commit sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='COMMIT_SELL',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
