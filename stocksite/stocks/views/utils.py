"""
Utilities file for stocks API.
"""
import socket
import sys
from time import time

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

    def getQuote(username, stockSymbol, mockCryptoKey=mockCryptoKey):
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

            cache.hmset(stockSymbol, quote_data)
            cache.expire(stockSymbol, CACHE_TTL)

            return quote_data
        else:
            quote_data['price'] = float(quote_data['price'])
            quote_data['quoteServerTime'] = float(quote_data['quoteServerTime'])
            return quote_data
            


""" The quote server. Will return an actual quote."""


class QuoteServer:
    QUOTE_PORT = 4444
    QUOTE_HOST_NAME = '192.168.4.2'

    def __init__(self, port=QUOTE_PORT, hostname=QUOTE_HOST_NAME):
        self.port = port
        self.hostname = hostname

    def connect(self):
        """
        Connect to quote server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            print(f"Connecting to {self.hostname}:{self.port} ...")
            self.socket.connect((self.hostname, self.port))

        except socket.error as err:
            print(f"ERROR! binding port {self.port} failed with error: {err}")
            self.socket.close()
            sys.exit(1)

    def getQuote(self, username, stockSymbol):
        """
            Get a quote from the quote server
        """

        # First check the cache for quote
        quote_data = cache.hgetall(stockSymbol)

        if not quote_data:
            # Connect to quote server
            self.connect()

            # Get query and send to quote server
            quote = username + ',' + stockSymbol + "\n"

            self.socket.send(quote.encode())

            # Read and send back 1k of data.
            try:

                data = self.socket.recv(1024)
                data = data.decode().split(",")

                quote_data = {
                    'price': data[0],
                    'stockSymbol': data[1],
                    'user': data[2],
                    'quoteServerTime': data[3],
                    'cryptokey': data[4]
                }

                cache.hmset(stockSymbol, quote_data)
                cache.expire(stockSymbol, CACHE_TTL)

                # close quote server connection and send back data
                self.socket.close()
                return quote_data

            except:
                print('Connection to server closed')
                # close the connection, and the socket
                self.socket.close()
        else:
            quote_data['price'] = float(quote_data['price'])
            quote_data['quoteServerTime'] = int(quote_data['quoteServerTime'])
            return quote_data


def getByStockSymbol(stocks, stockSymbol):
    """
    Searches for the dictionary containing the correct stockSymbol in the list.
    """
    return next((item for item in stocks if item['stockSymbol'] == stockSymbol), None)
