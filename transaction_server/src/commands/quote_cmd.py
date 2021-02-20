import sys
import time
import pymongo

from .db_log import dbLog

sys.path.append('..')
from quoteServer import MockQuoteServer, QuoteServer


ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'

class QuoteCmd():
    def execute(self, cmdDict):
        """
            Retrieves price of stock
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Create quote server (Note: this is the actual version for VM, use mock quote server for local testing by changing to MockQuoteServer instead)
            qs = MockQuoteServer()

            # query the quote server
            quote_data = qs.getQuote(cmdDict)
            
            # Log the results from quote server
            cmdDict['price'] = quote_data['price']
            cmdDict['cryptokey'] = quote_data['cryptokey']
            cmdDict['timestamp'] = quote_data['timestamp']

            dbLog.log(cmdDict, QUOTE_LOG)

            # return the current price of shares
            return float(quote_data['price'])
        except:
            pass
