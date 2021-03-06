""" Handles all the logging of commands into the transaction collection """

import time
import sys
import pymongo

from .database import Database

TRANSACT_COLLECT = "transactions"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'
QUOTE_LOG = 'quoteServer'


class dbLog():
    def log(cmdDict, kind, error=None):
        """
            Log the commands into transaction collection
        """

        cmdDict['timestamp'] = str(int(time.time() * 1000))
        cmdDict['logType'] = kind
        cmdDict['_id'] = cmdDict['transactionNumber'] + cmdDict['user'] + cmdDict['command'] + cmdDict['timestamp'] + cmdDict['logType']

        if (error != None):
            cmdDict['errorMessage'] = error

        try:
            Database.insert(TRANSACT_COLLECT, cmdDict)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not log command into database. Failed with: {err}")

    def logQuote(cmdDict):
        """
            Log the quote commands into transaction collection
        """

        try:
            Database.insert(TRANSACT_COLLECT, cmdDict)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not log command into database. Failed with: {err}")
