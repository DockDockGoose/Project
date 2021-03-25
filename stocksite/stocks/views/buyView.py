from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from accounts.serializers import AccountSerializer
from django.core import serializers
from transactions.models import Transaction
from stocks.models import Stock
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
        username = request.data.get("username")
        stockSymbol = request.data.get("stockSymbol")
        amount = float(request.data.get("amount"))
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")


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

        # Find user account

        if username in cache:
            account = cache.get(username)
            account = json.loads(account)
        else:
            account = Account.objects.filter(username=username).first()

            # change account to string in order to cache
            new_account = {
                'username': account.username,
                'funds': account.funds,
                'pendingFunds': account.pendingFunds,
                'stocks': account.stocks,
                'buy': account.buy,
                'sell': account.sell,
            }

            str_account = json.dumps(new_account)
            cache.set(username, str_account)

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
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

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
                errorMessage='Insufficient funds :(.',
            )
            transaction.save()
            return Response("Insufficient funds :(.", status=status.HTTP_412_PRECONDITION_FAILED)

        
        # TODO: Check for quote in cache (if not in cache/is stale perform query)
        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = MockQuoteServer.getQuote(username, stockSymbol)

        # Set a buy command to the user
        newStock = {'stockSymbol':stockSymbol, 'price':quoteQuery['price'], 'quoteServerTime':quoteQuery['quoteServerTime'], 'sharesAmount':amount/quoteQuery['price']}
        account.buy = newStock
        account.save()

        return Response(status=status.HTTP_200_OK)
