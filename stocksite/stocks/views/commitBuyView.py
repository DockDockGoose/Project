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
        # Test values (uncomment to populate the db)
        # stockSymbol = 'NISSAN'
        # amount = 500.00
        
        # Check cache for recent buy transaction (within 60 sec), if non-existent log errorEvent
        # stockSymbol = fromcache
        # amount = fromcache

        # Find user account
        account = Account.objects.filter(username=username).first()
        
        # TODO: Check for quote in cache (if not in cache/is stale perform query)
        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)

        # Remove amount from account funds
        account.funds -= amount

        # Search account for stock
        stock = getByStockSymbol(account.stocks, stockSymbol)

        # Create new stock in account if non-existing
        if stock is None:
            newStock = {'stockSymbol':stockSymbol, 'price':quoteQuery['price'], 'quoteServerTime':quoteQuery['quoteServerTime'], 'sharesAmount':amount/quoteQuery['price']}
            account.stocks.append(newStock)
        else:
            # If stock exists in account, add amount/price to stock sharesAmount
            stock['sharesAmount'] += amount/quoteQuery['price']

        account.save()

        # Log commit buy transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='COMMIT_BUY',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
