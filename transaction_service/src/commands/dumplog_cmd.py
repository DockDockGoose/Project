import sys
import pymongo
import redis

sys.path.append('../../')

from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')

ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'

class DumplogCmd():
    def execute(cmdDict):
        """
            Print all of the transactions or just the user's transactions
        """
        dbLog.log(cmdDict, CMD_LOG)        

        try:
            # Get entire log or use log
            if 'user' in cmdDict.keys():
                transactions = list(Database.find(TRANSACT_COLLECT, {'user': cmdDict['user']}))
                if (transactions == None):
                    err = "Invalid cmd. Transactions did not exist for user." 
                    dbLog.log(cmdDict, ERROR_LOG, err)
                    exit(1)
            else:
                transactions = list(Database.find(TRANSACT_COLLECT))
                if (transactions == None):
                    err = "Invalid cmd. Transactions did not exist." 
                    dbLog.log(cmdDict, ERROR_LOG, err)
                    exit(1)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)

        try:
            with open(cmdDict['filename'], 'w') as f:
                for transact in transactions:
                    f.write("%s\n" % transact)
        except IOError:
            print("Error while trying to open and write to", cmdDict['filename'])
            
        f.close()