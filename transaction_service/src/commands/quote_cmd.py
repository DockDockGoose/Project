import sys
import time
import pymongo

from .db_log import dbLog

sys.path.append('..')
from ..quoteServer import MockQuoteServer, QuoteServer


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
            qs = MockQuoteServer()

            # query the quote server
            quote_data = qs.getQuote(cmdDict)

            # Log the results from quote server
            quote_data['command'] = 'QUOTE'
            quote_data['logType'] = QUOTE_LOG

            dbLog.logQuote(quote_data)

            # return the current price of shares
            return float(quote_data['price'])
        except:
            pass

    def systemExecute(cmdDict):
        """
            Retrieves price of stock for system triggers
                - does not contain the logging
        """

        try:
            # Create quote server (Note: this is the actual version for VM, use mock quote server for local testing by changing to MockQuoteServer instead)
            qs = MockQuoteServer()

            # query the quote server
            quote_data = qs.getQuote(cmdDict)

            # Log the results from quote server
            quote_data['command'] = 'QUOTE'
            quote_data['logType'] = SYSTEM_LOG

            dbLog.logQuote(quote_data)

            # return the current price of shares
            return float(quote_data['price'])
        except:
            pass
