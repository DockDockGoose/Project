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

CACHE_TTL = 60

class CommitBuyView(APIView):
    """
    API endpoint for confirming the buy of a stock.
    """
    def post(self, request):
        # Get request data
        username = request.data.get("username")
        transactionNum = request.data.get("transactionNum")
        command = request.data.get("command")

        # Log commit buy transaction
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

        # key buy command from cache
        key = username + 'buy'

        buy_cmd = cache.hgetall(key)

        # delete buy command from cache
        cache.hdel(*key)

        # Check that user has buy command
        if not buy_cmd:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                errorMessage='Buy command does not exist.',
            )
            transaction.save()
            return Response("Buy command doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Remove amount from account funds
        account.funds -= float(buy_cmd['price']) * float(buy_cmd['sharesAmount'])

        # Check if user has any stocks
        if account.stocks is None:
            newStock = {
                'stockSymbol':buy_cmd['stockSymbol'],
                'price':buy_cmd['price'],
                'quoteServerTime':buy_cmd['quoteServerTime'],
                'sharesAmount':buy_cmd['sharesAmount']
                }
            account.stocks = [newStock]
        else:
            # Else search account for stock
            stock = getByStockSymbol(account.stocks, buy_cmd['stockSymbol'])

            # Create new stock in account if non-existing
            if stock is None:
                newStock = {
                    'stockSymbol':buy_cmd['stockSymbol'],
                    'price':buy_cmd['price'],
                    'quoteServerTime':buy_cmd['quoteServerTime'],
                    'sharesAmount':buy_cmd['sharesAmount']
                }
                account.stocks.append(newStock)
            else:
                # If stock exists in account, add amount/price to stock sharesAmount
                stock['sharesAmount'] += float(buy_cmd['sharesAmount'])
        
        # Log account transaction 
        transaction = Transaction(
                type='accountTransactions',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                action='remove',
                username=username,
                amount= float(buy_cmd['price']) * float(buy_cmd['sharesAmount']),
            )
        transaction.save()
        
        account.save()

        return Response(status=status.HTTP_200_OK)
