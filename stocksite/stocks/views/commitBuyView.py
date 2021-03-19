from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .utils import MockQuoteServer, getByStockSymbol
from time import time


class CommitBuyView(APIView):
    """
    API endpoint for confirming the buy of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # Log commit buy transaction
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
        # amount = 500.00
        
        # Check cache for recent buy transaction (within 60 sec), if non-existent log errorEvent
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

        # Check that user has buy command
        if account.buy is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Buy command does not exist.',
            )
            transaction.save()
            return Response("Buy command doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Remove amount from account funds
        account.funds -= account.buy['price'] * account.buy['sharesAmount']

        # Check if user has any stocks
        if account.stocks is None:
            newStock = {'stockSymbol':account.buy['stockSymbol'], 'price':account.buy['price'], 'quoteServerTime':account.buy['quoteServerTime'], 'sharesAmount':account.buy['sharesAmount']}
            account.stocks = [newStock]
        else:
            # Else search account for stock
            stock = getByStockSymbol(account.stocks, account.buy['stockSymbol'])

            # Create new stock in account if non-existing
            if stock is None:
                newStock = {'stockSymbol':account.buy['stockSymbol'], 'price':account.buy['price'], 'quoteServerTime':account.buy['quoteServerTime'], 'sharesAmount':account.buy['sharesAmount']}
                account.stocks.append(newStock)
            else:
                # If stock exists in account, add amount/price to stock sharesAmount
                stock['sharesAmount'] += account.buy['sharesAmount']
        
        # Log account transaction 
        transaction = Transaction(
                type='accountTransactions',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='remove',
                username=username,
                amount=account.buy['price'] * account.buy['sharesAmount'],
            )
        transaction.save()
        
        # Remove buy command from user's account
        account.buy = None
        account.save()

        return Response(status=status.HTTP_200_OK)
