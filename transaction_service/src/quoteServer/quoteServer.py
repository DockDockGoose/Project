""" Used to query quotes from the quote server. """

import socket
import sys
import redis

sys.path.append('../../')
from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')


QUOTE_PORT = 4444
QUOTE_HOST_NAME = '192.168.4.2'

PACKET_SIZE = 1024
CACHE_TTL = 60


class QuoteServer:

    def __init__(self, hostname=QUOTE_HOST_NAME, port=QUOTE_PORT, ):

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

    def getQuote(self, cmdDict):
        """
            Get a quote from the quote server
        """

        # Check for stock 
        quote_data = cache.hgetall(cmdDict['stockSymbol'])

        if not quote_data:

            # Connect to quote server
            self.connect()

            # Get query and send to quote server
            quote = cmdDict['stockSymbol'] + ',' + cmdDict['user'] + "\n"

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
                    'cryptokey': data[4]
                }

                # Add quote data to cache for 60s
                cache.hmset(cmdDict['stockSymbol'], quote_data)
                cache.expire(cmdDict['stockSymbol'], CACHE_TTL)

                dbLog.logQuote(quote_data)

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
