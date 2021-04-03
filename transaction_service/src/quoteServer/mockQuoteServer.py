""" A mock up of the quote server. Will return dummy quote."""

import time
import sys
import redis

sys.path.append('../../')
from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')

CACHE_TTL = 60 

class MockQuoteServer:
    QUOTE_PORT = 65432
    QUOTE_HOST_NAME = '127.0.0.1'

    def __init__(self, port=QUOTE_PORT, hostname=QUOTE_HOST_NAME):
        self.port = port
        self.hostname = hostname

    def getQuote(self, cmdDict):
        """
            Use intead of getQuote when you are not connected to server
            Will return dummy data.
        """
        # First check the cache for quote
        quote_data = cache.hgetall(cmdDict['stockSymbol'])

        if not quote_data:

            time.sleep(0.05)
            quote_data = {
                'price': '10',
                'stockSymbol': cmdDict['stockSymbol'],
                'user': cmdDict['user'],
                'quoteServerTime': str(int(time.time() * 1000)),
                'cryptokey': 'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools='
            }

            # Add quote data to cache for 60s
            cache.hmset(cmdDict['stockSymbol'], quote_data)
            cache.expire(cmdDict['stockSymbol'], CACHE_TTL)

            return quote_data
        else:
            quote_data['price'] = float(quote_data['price'])
            quote_data['quoteServerTime'] = int(quote_data['quoteServerTime'])
            return quote_data
