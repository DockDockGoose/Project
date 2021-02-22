""" A mock up of the quote server. Will return dummy quote."""

import time


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
        time.sleep(0.05)
        quote_data = {
            'price': '10',
            'stockSymbol': cmdDict['stockSymbol'],
            'user': cmdDict['user'],
            'quoteServerTime': str(int(time.time() * 1000)),
            'cryptokey': 'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools='
        }

        return quote_data
