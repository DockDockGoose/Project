from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .utils import getByStockSymbol
from time import time

from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

class CommitSellView(APIView):
    """
    API endpoint for confirming the sell of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # Log commit Sell transaction
        transaction = Transaction(
                type='userCommand',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
            )
        transaction.save()

        # Find user account
        account = Account.objects.filter(username=username).first()

        # Get sell command from cache
        key = username + 'sell'

        sell_cmd = cache.hgetall(key)

        # delete sell command from cache
        cache.hdel(*key)

        # If account is non-existing, log errorEvent to Transaction
        if account is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check that user has sell command
        if not sell_cmd:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Sell command does not exist.',
            )
            transaction.save()
            return Response("Sell command doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Search account for stock
        stock = getByStockSymbol(account.stocks, sell_cmd['stockSymbol'])

        # Subtract amount from stock sharesAmount & add amount to account funds
        stock['sharesAmount'] -= float(sell_cmd['sharesAmount'])
        account.funds += float(sell_cmd['sharesAmount']) * float(sell_cmd['price'])

        # Log account transaction 
        transaction = Transaction(
                type='accountTransactions',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='add',
                username=username,
                amount= float(sell_cmd['sharesAmount']) * float(sell_cmd['price']),
            )
        transaction.save()
        
        # Update account
        account.save()

        return Response(status=status.HTTP_200_OK)
