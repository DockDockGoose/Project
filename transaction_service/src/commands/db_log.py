import time
import sys
import pymongo

from ..database.database import Database

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
        # Want to keep timestamp from quote server for quote server actions

        cmdDict['timestamp'] = str(int(time.time() * 1000))
        cmdDict['logType'] = kind
        cmdDict['_id'] = cmdDict['user'] + cmdDict['command'] + cmdDict['timestamp'] + cmdDict['logType']

        if (error != None):
            cmdDict['errorMessage'] = error

        try:
            Database.insert(TRANSACT_COLLECT, cmdDict)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not log command into database. Failed with: {err}")

    def logQuote(cmdDict):

        try:
            Database.insert(TRANSACT_COLLECT, cmdDict)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not log command into database. Failed with: {err}")