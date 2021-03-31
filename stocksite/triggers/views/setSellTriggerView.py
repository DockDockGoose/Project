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


class SetSellTriggerView(APIView):
    """
    API endpoint that sets sell trigger price.
    """
    def put(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # First log set sell trigger command
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

        # Check if stock had a previous trigger
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
                amount=amount,
                errorMessage='Sell trigger does not exist.',
            )
            transaction.save()
            return Response("Sell trigger does not exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Update trigger to include trigger price
        trigger_data['price'] = amount
        cache.hmset(key, trigger_data)

        # Decrease the number of stock shares in user's account 
        account = Account.objects.filter(username=username).first()
        stock = getByStockSymbol(account.stocks, stockSymbol)
        stock['sharesAmount'] -= float(trigger_data['sharesAmount']) * amount

        account.save()

        # Also log account transaction change
        transaction = Transaction(
                type='accountTransaction',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='remove',
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
