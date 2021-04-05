from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from triggers.models import Trigger
from .utils import getByStockSymbol
from time import time
from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class CancelSetSellView(APIView):
    """
    API endpoint that sets sell trigger price.
    """
    def delete(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # First log cancel set sell command
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
        
        # Find previous sell trigger
        key = username + stockSymbol + 'sell'
        trigger_data = cache.hgetall(key)

        # If trigger is non-existing, log errorEvent to Transaction
        if not trigger_data:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                errorMessage='Sell trigger does not exist.',
            )
            transaction.save()
            return Response("Sell trigger does not exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Decrease the number of stock shares in user's account 
        account = Account.objects.filter(username=username).first()
        stock = getByStockSymbol(account.stocks, stockSymbol)
        stock['sharesAmount'] += float(trigger_data['sharesAmount']) * float(trigger_data['price'])

        account.save()

        # Delete trigger
        cache.hdel(*key)

        # Also log account transaction change
        transaction = Transaction(
                type='accountTransaction',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='add',
                username=username,
                stockSymbol=stockSymbol,
                amount=float(trigger_data['sharesAmount']) * float(trigger_data['price']),
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
