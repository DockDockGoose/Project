"""
Utilities file for stocks API.
"""
import socket
import sys
from time import time
from transactions.models import Transaction
from django.conf import settings
import redis

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                          db=0)

CACHE_TTL = 60

""" A mock up of the quote server. Will return dummy quote."""


class MockQuoteServer:
    QUOTE_PORT = 65432
    QUOTE_HOST_NAME = '127.0.0.1'
    mockCryptoKey = 'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools'

    def __init__(self, port=QUOTE_PORT, hostname=QUOTE_HOST_NAME):
        self.port = port
        self.hostname = hostname

    def getQuote(self, username, stockSymbol, transactionNum, mockCryptoKey=mockCryptoKey):
        """
            Use intead of getQuote when you are not connected to server
            Will return dummy data.
        """
        # First check the cache for quote
        quote_data = cache.hgetall(stockSymbol)
        
        if not quote_data:
            quote_data = {
                'price': 10.50,
                'stockSymbol': stockSymbol,
                'username': username,
                'quoteServerTime': int(time() * 1000),
                'cryptoKey': mockCryptoKey
            }
            #  Log quoteServer transaction (only increment transactionNum for userCommands?)
            transaction = Transaction(
                    type='quoteServer',
                    timestamp=int(time()*1000),
                    server='DOCK1',
                    transactionNum=transactionNum,
                    price=quote_data['price'],
                    username=username,
                    stockSymbol=stockSymbol,
                    quoteServerTime=int(quote_data['quoteServerTime']),
                    cryptoKey=quote_data['cryptoKey']
                )
            transaction.save()

            cache.hmset(stockSymbol, quote_data)
            cache.expire(stockSymbol, CACHE_TTL)

            return quote_data
        else:
            #  Log system event for caching quote
            transaction = Transaction(
                type='systemEvent',
                timestamp=int(time()*1000),
                server='DOCK1',
                transactionNum=transactionNum,
                command='CachedQuote',
                amount=quote_data['price'],
                username=username,
                stockSymbol=stockSymbol,
            )
            transaction.save()
            
            quote_data['price'] = float(quote_data['price'])
            quote_data['quoteServerTime'] = int(quote_data['quoteServerTime'])
            return quote_data
            

def getByStockSymbol(stocks, stockSymbol):
    """
    Searches for the dictionary containing the correct stockSymbol in the list.
    """
    return next((item for item in stocks if item['stockSymbol'] == stockSymbol), None)
