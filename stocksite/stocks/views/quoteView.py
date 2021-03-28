from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from .utils import MockQuoteServer
from .quoteHandler import QuoteServer
from time import time

from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
 
CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class QuoteView(APIView):
    """
    API endpoint that allows a stock to be quoted.
    """
    def get(self, request):
        stockSymbol     = request.data.get('stockSymbol')
        username        = request.data.get('username')
        transactionNum  = request.data.get('transactionNum')
        command         =  request.data.get('command')

        # Log the quote command transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum=transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
            )
        transaction.save()

        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        # quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)
        qs = QuoteServer()    
        quoteQuery = qs.getQuote(stockSymbol, username)
        # TODO: Cache the recently quoted stock price

        #  Log quoteServer transaction (only increment transactionNum for userCommands?)
        transaction = Transaction(
                type='quoteServer',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                price=quoteQuery['price'],
                username=username,
                stockSymbol=stockSymbol,
                quoteServerTime=int(quoteQuery['quoteServerTime']),
                cryptoKey=quoteQuery['cryptoKey']
            )

        transaction.save()

        return Response(quoteQuery, status=status.HTTP_200_OK)
