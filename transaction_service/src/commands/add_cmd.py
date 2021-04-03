import pymongo
import sys
import redis

sys.path.append('../../')

from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')

ACCOUNTS_COLLECT = "accounts"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class AddCmd:
    def execute(cmdDict):
        """
            Adds money to user's account
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if new user
            key = cmdDict['user']
            account = cache.hgetall(key)
            if not account:
                # Modify command to get appropriate information for database
                user_data = {
                    '_id': cmdDict['user'],
                    'funds': cmdDict['amount']
                }
                cache.hmset(key, user_data)
            else:
                # Update the current user funds
                user_data = {
                    '_id': cmdDict['user'],
                    'funds': float(account['funds']) + cmdDict['amount']
                }
                cache.hmset(key, user_data)

            dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)
