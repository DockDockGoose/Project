import time
import sys
import pymongo

sys.path.append('..')
from database.database import Database

TRANSACT_COLLECT = "transactions"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class dbLog():
    def log(self, cmdDict, type, error=None):
        """
            Log the commands into transaction collection
        """
        cmdDict['timestamp'] = str(int(time.time() * 1000))
        cmdDict['logType'] = type

        if (error != None):
            cmdDict['errorMessage'] = error

        try:
            Database.insert(TRANSACT_COLLECT, cmdDict)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not log command into database. Failed with: {err}")
