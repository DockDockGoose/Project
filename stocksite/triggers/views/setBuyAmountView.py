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


class SetBuyAmountView(APIView):
    """
    API endpoint that sets buy amount triggers.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # Log set buy amount transaction
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
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not exist for buy trigger.',
            )
            transaction.save()
            return Response("Account doesn't exist for buy trigger.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if funds permit action, log error event to transaction if not
        if account.funds < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Insufficient funds for buy trigger :(.',
            )
            transaction.save()
            return Response("Insufficient funds for buy trigger :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if stock had a previous trigger
        key = username + stockSymbol + 'buy'
        trigger_data = cache.hgetall(key)

        if not trigger_data:
            # Add new trigger buy command
            trigger = Trigger(key=key,username=username, type='buy', stockSymbol=stockSymbol, sharesAmount=amount)
        else:
            # Update the stocks buy trigger command
            trigger['sharesAmount'] = amount
        cache.hmset(key, trigger_data)


        # Remove funds from user account and put into pending
        account.funds -= amount
        account.pendingFunds += amount
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
