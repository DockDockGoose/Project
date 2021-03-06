""" Used to query quotes from the quote server. """
import socket
import sys
from time import time
from transactions.models import Transaction
from django.conf import settings
import redis

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                          db=0)
CACHE_TTL = 60
QUOTE_PORT = 4444
QUOTE_HOST_NAME = '192.168.4.2'
PACKET_SIZE = 1024


class QuoteServer:

    def __init__(self, hostname=QUOTE_HOST_NAME, port=QUOTE_PORT):
        self.hostname = hostname
        self.port = port

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

    def getQuote(self, username, stockSymbol, transactionNum):
        """
            Get a quote from the quote server
        """
        # First check the cache for quote
        quote_data = cache.hgetall(stockSymbol)

        if not quote_data:
            # Connect to quote server
            self.connect()

            # Get query and send to quote server
            quote = stockSymbol + ',' + username + "\n"

            self.socket.send(quote.encode())

            # Read and send back 1k of data.
            try:

                data = self.socket.recv(PACKET_SIZE)
                data = data.decode().split(",")

                quote_data = {
                    'price': data[0],
                    'stockSymbol': data[1],
                    'user': data[2],
                    'quoteServerTime': data[3],
                    'cryptoKey': data[4]
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
                
                # Add quote data to cache for 60s
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

