from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from transactions.models import Transaction
from triggers.models import Trigger
from time import time
from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


class SetBuyTriggerView(APIView):
    """
    API endpoint that sets buy price triggers.
    """
    def put(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # First log set buy trigger
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
        key = username + stockSymbol + 'buy'
        trigger_data = cache.hgetall(key)

        # If account is non-existing, log errorEvent to Transaction
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
                errorMessage='Buy trigger does not exist.',
            )
            transaction.save()
            return Response("Buy trigger doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Update trigger to include trigger price
        trigger_data["price"] = amount
        cache.hmset(key, trigger_data)

        return Response(status=status.HTTP_200_OK)
