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
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # Log commit Sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
            )
        transaction.save()
        # Test values (uncomment to populate the db)
        # stockSymbol = 'NISSAN'
        # amount = 300.00
        
        # Check cache for recent sell transaction (within 60 sec), if non-existent log errorEvent
        # stockSymbol = fromcache
        # amount = fromcache

        # Find user account
        account = Account.objects.filter(username=username).first()

        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check that user has sell command
        if account.sell is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Sell command does not exist.',
            )
            transaction.save()
            return Response("Sell command doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Search account for stock
        stock = getByStockSymbol(account.stocks, account.sell['stockSymbol'])

        # Subtract amount from stock sharesAmount & add amount to account funds
        stock['sharesAmount'] -= account.sell['sharesAmount']
        account.funds += account.sell['sharesAmount'] * account.sell['price']

        # Log account transaction 
        transaction = Transaction(
                type='accountTransactions',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='add',
                username=username,
                amount=account.sell['sharesAmount'] * account.sell['price'],
            )
        transaction.save()
        
        # Remove buy command from user's account
        account.sell = None
        account.save()

        

        return Response(status=status.HTTP_200_OK)
