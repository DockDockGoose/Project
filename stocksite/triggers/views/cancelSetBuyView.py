from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from triggers.models import Trigger
from time import time
from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)



class CancelSetBuyView(APIView):
    """
    API endpoint that cancels a buy trigger.
    """
    def delete(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # First log cancel set buy command
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

        # Find previous buy trigger
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
                errorMessage='Buy trigger does not exist.',
            )
            transaction.save()
            return Response("Buy trigger doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)
        
        # Find user account
        account = Account.objects.filter(username=username).first()

        # Add funds back into user account
        account.pendingFunds -= float(trigger_data['sharesAmount'])
        account.funds += float(trigger_data['sharesAmount'])
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
                amount=float(trigger_data['sharesAmount']),
            )
        transaction.save()

        return Response(status=status.HTTP_200_OK)
