from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .utils import MockQuoteServer, getByStockSymbol
from time import time

from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class CancelBuyView(APIView):
    """
    API endpoint for cancelling the buy of a stock.
    """
    def delete(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # First log the delete sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
            )
        transaction.save()

        # Delete buy command from the cache
        key = username + 'buy'

        cache.hdel(*key)
    
        return Response(status=status.HTTP_200_OK)
