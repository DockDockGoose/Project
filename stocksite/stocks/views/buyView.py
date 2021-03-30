from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from accounts.serializers import AccountSerializer
from django.core import serializers
from transactions.models import Transaction
from stocks.models import Stock
from .quoteHandler import QuoteServer
from .utils import MockQuoteServer
from time import time

from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

CACHE_TTL = 60

class BuyView(APIView):
    """
    API endpoint that allows stocks to be bought.
    """
    def put(self, request):
        # Get request data
        username        = request.data.get("username")
        stockSymbol     = request.data.get("stockSymbol")
        amount          = float(request.data.get("amount"))
        transactionNum  = request.data.get("transactionNum")
        command         = request.data.get("command")


        # First thing log buy transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        # TODO: Check for quote in cache (if not in cache/is stale perform query)
        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = QuoteServer.getQuote(username, stockSymbol)

        # Add a new buy command
        new_stock = {
            'key': username + 'buy',
            'stockSymbol':stockSymbol,
            'price':quoteQuery['price'],
            'quoteServerTime':quoteQuery['quoteServerTime'],
            'sharesAmount':amount/float(quoteQuery['price']),
        }
        
        # Set to cache and set expiration for 60 secondss
        cache.hmset(new_stock['key'], new_stock)
        cache.expire(new_stock['key'], CACHE_TTL)

        return Response(status=status.HTTP_200_OK)
