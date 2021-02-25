from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from .utils import MockQuoteServer
from time import time


class QuoteView(APIView):
    """
    API endpoint that allows a stock to be quoted.
    """
    def get(self, request):
        stockSymbol = request.data.get('stockSymbol')
        username = request.data.get('username')

        # Log the quote command transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum + 1,
                command='QUOTE',
                username=username,
                stockSymbol=stockSymbol,
            )
        transaction.save()

        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)
        # TODO: Cache the recently quoted stock price

        #  Log quoteServer transaction (only increment transactionNum for userCommands?)
        transaction = Transaction(
                type='quoteServer',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = Transaction.objects.last().transactionNum,
                price=quoteQuery['price'],
                username=username,
                stockSymbol=stockSymbol,
                quoteServerTime=quoteQuery['quoteServerTime'],
                cryptoKey=quoteQuery['cryptoKey']
            )
        transaction.save()

        return Response(quoteQuery, status=status.HTTP_200_OK)
