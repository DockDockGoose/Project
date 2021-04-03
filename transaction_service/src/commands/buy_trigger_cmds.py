import sys
import pymongo
import redis

sys.path.append('../../')

from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')

ACCOUNTS_COLLECT = "accounts"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class SetBuyAmtCmd():
    def execute(cmdDict):
        """
            Creates a buy trigger based on the number of the stocks the user wants to buy
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Make sure user exist and has enough funds in accountt
            user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})

            if (user_funds == None):
                err = "Invalid cmd. User does not exist." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

            elif (user_funds['funds'] >= cmdDict['amount']):
                # Add new trigger buy command and remove funds from user account
                buy_trigger = {
                    'user': cmdDict['user'],
                    'type': 'buy',
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount']
                }

                key = cmdDict['user'] + cmdDict['stockSymbol'] + 'buy'
                cache.hmset(key, buy_trigger)

                # Decrease user's funds
                account = cache.hgetall(cmdDict['user'])
                account['funds'] = float(account['funds']) - cmdDict['amount']
                cache.hmset(cmdDict['user'], account)

                dbLog.log(cmdDict, TRANSACT_LOG) 
            else:
                err = "Invalid cmd. User has insufficient funds." 
                dbLog.log(cmdDict, ERROR_LOG, err)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 

class CancelSetBuyCmd():
    def execute(cmdDict):
        """
            Cancels the set buy command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already set buy amount for the stock
            key = cmdDict['user'] + cmdDict['stockSymbol'] + 'buy'
            buy_trigger = cache.hgetall(key)

            if not buy_trigger:
                err = "Invalid cmd. User does not have a buy trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

            else:
                # Add funds back to user's account and delete set_buy trigger
                account = cache.hgetall(cmdDict['user'])
                account['funds'] = float(account['funds']) + float(buy_trigger['amount'])
                cache.hmset(cmdDict['user'], account)

                # Delete trigger
                cache.hdel(*key)
                cmdDict['amount'] = float(buy_trigger['amount'])
                dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)

class SetBuyTriggerCmd():
    def execute(cmdDict):
        """
            Adds the price trigger to the set buy command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already set buy amount for the stock
            key = cmdDict['user'] + cmdDict['stockSymbol'] + 'buy'
            buy_trigger = cache.hgetall(key)
            
            if  not buy_trigger:
                err = "Invalid cmd. User does not have a trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Add trigger point
                buy_trigger['triggerPrice'] = cmdDict['amount']
                cache.hmset(key, buy_trigger)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 

