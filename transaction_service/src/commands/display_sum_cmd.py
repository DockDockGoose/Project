import sys
import pymongo

from .db_log import dbLog

from ..database.database import Database

ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class DisplaySumCmd():
    def execute(cmdDict):
        """
            Print the user's account from accounts, transaction history, and buy/sell triggers
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            user_transactions = list(Database.find(TRANSACT_COLLECT, {'user': cmdDict['user']}))

            user_account = list(Database.find(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}))

            user_triggers = list(Database.find(TRIGGER_COLLECT, {'user': cmdDict['user']}))

            if (user_transactions == None):
                err = "Invalid cmd. User does not exist." 
                dbLog.log(cmdDict, ERROR_LOG, err)
                exit(1)
            
        # print("----- User's Transaction History -----\n", user_transactions)
        # print("\n----- User's Current Account Status -----\n", user_account)
        # print("\n----- User's Triggers -----\n", user_triggers)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 
        