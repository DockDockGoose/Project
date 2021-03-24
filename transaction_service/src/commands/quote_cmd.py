import sys
import time
import pymongo

sys.path.append('../')
from ..quoteServer import MockQuoteServer, QuoteServer

sys.path.append('../')

from database.src.database import Database
from database.src.db_log import dbLog


ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'
SYSTEM_LOG = 'systemEventType'

class QuoteCmd():
    def execute(cmdDict):
        """
            Retrieves price of stock
        """

        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Create quote server (Note: this is the actual version for VM, use mock quote server for local testing by changing to MockQuoteServer instead)
            qs = QuoteServer()

            # query the quote server
            quote_data = qs.getQuote(cmdDict)

            # Log the results from quote server
            quote_data['command'] = 'QUOTE'
            quote_data['logType'] = QUOTE_LOG
            quote_data['transactionNumber'] = cmdDict['transactionNumber']
            quote_data['server'] = cmdDict['server']
            quote_data['timestamp'] = str(int(time.time() * 1000))

            dbLog.logQuote(quote_data)

            # return the current price of shares
            return float(quote_data['price'])
        except TypeError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)
