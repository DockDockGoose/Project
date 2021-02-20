import pymongo

from .db_log import dbLog
from database.database import Database

ACCOUNTS_COLLECT = "accounts"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class AddCmd:
    def execute(self, cmdDict):
        """
            Adds money to user's account
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if new user
            if (Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}) == None):
                # Modify command to get appropriate information for database
                user_data = {
                    '_id': cmdDict['user'],
                    'funds': cmdDict['amount']
                }
                Database.insert(ACCOUNTS_COLLECT, user_data)
            else:
                # Update the current user funds
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': { 'funds': cmdDict['amount']}})

            dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)
