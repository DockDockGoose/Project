from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from accounts.models import Account
from transactions.models import Transaction
from .quoteHandler import QuoteServer
from .utils import MockQuoteServer, getByStockSymbol
from time import time

from django.conf import settings
import redis
import json

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

CACHE_TTL = 60

class SellView(APIView):
    """
    API endpoint that allows stocks to be sold.
    """
    def put(self, request):
        # Get request data
        username        = request.data.get("username")
        stockSymbol     = request.data.get("stockSymbol")
        amount          = float(request.data.get("amount"))
        transactionNum  = request.data.get("transactionNum")
        command         = request.data.get("command")

        # First thing log sell transaction
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
                errorMessage='Account does not exist.',
            )
            transaction.save()
            return Response("Account doesn't exist.", status=status.HTTP_412_PRECONDITION_FAILED)

        # If user does not have any stocks
        if account.stocks is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Account does not have stocks.',
            )
            transaction.save()
            return Response("Account does not have stocks.", status=status.HTTP_412_PRECONDITION_FAILED)
            
        # Search Account for stock, log error event to transaction if doesnt exist
        stock = getByStockSymbol(account.stocks, stockSymbol)

        if stock is None:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Stock not owned.',
            )
            transaction.save()
            return Response("Stock not owned.", status=status.HTTP_412_PRECONDITION_FAILED)

        # Check if shares amount permit action, or error event to transaction if not 
        sharesAmount = stock['sharesAmount']
        if sharesAmount < amount:
            transaction = Transaction(
                type='errorEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum = transactionNum,
                command=command,
                username=username,
                stockSymbol=stockSymbol,
                amount=amount,
                errorMessage='Not enough shares to sell.',
            )
            transaction.save()
            return Response("Not enough shares to sell.", status=status.HTTP_412_PRECONDITION_FAILED)

        # TODO: Check for quote in cache (if not in cache/is stale perform query)
        # Query the QuoteServer (Try/Catch for systemEvent/errorEvent logging)
        quoteQuery = QuoteServer.getQuote(username, stockSymbol)

        # Set a sell command to the cache
        new_stock = {
            'key': username + 'sell',
            'stockSymbol': stockSymbol,
            'price': quoteQuery['price'],
            'quoteServerTime': quoteQuery['quoteServerTime'],
            'sharesAmount': amount/float(quoteQuery['price']),
        }

        # Set to cache and set expiration for 60 secondss
        cache.hmset(new_stock['key'], new_stock)
        cache.expire(new_stock['key'], CACHE_TTL)

        return Response(status=status.HTTP_200_OK)
