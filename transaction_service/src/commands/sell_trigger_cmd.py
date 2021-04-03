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


class SetSellAmtCmd():
    def execute(cmdDict):
        """
            Creates a sell trigger based on the number of stocks the user wants to sell
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Get amount of stock from user
            stock_key = cmdDict['user'] + cmdDict['stockSymbol']
            user_stock = cache.hgetall(stock_key)

            if not user_stock:
                err = "Invalid cmd. User does not have the specified stock." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

            # Check if user has enough of stock in account and initialize sell trigger
            elif float(user_stock['amount']) >= cmdDict['amount']:
                sell_trigger = {
                    'user': cmdDict['user'],
                    'type': 'sell',
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount']
                }
                key = cmdDict['user'] + cmdDict['stockSymbol'] + 'sell'
                cache.hmset(key, sell_trigger)

            else:
                err = "Invalid cmd. User has insufficient amount of stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 


class CancelSetSellCmd():
    def execute(cmdDict):
        """
            Cancels the set sell command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already set sell amount for the stock
            key = cmdDict['user'] + cmdDict['stockSymbol'] + 'sell'
            sell_trigger = cache.hgetall(key)

            if not sell_trigger:
                err = "Invalid cmd. User does not have a sell trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Re-add funds only if trigger price had been set
                if ('triggerPrice' in sell_trigger.keys()):
                    stock_key = cmdDict['user'] + cmdDict['stockSymbol']
                    user_stock = cache.hgetall(stock_key)

                    user_stock['amount'] = float(user_stock['amount']) + (float(sell_trigger['amount']))
                    cache.hmset(stock_key, user_stock)

                    cmdDict['amount'] = float(sell_trigger['amount'])
                    dbLog.log(cmdDict, TRANSACT_LOG)
                    
                # Delete sell trigger
                cache.hdel(*key)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)


class SetSellTriggerCmd():
    def execute(cmdDict):
        """
            Adds the price trigger to the set sell command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already has set sell amount for the stock
            key = cmdDict['user'] + cmdDict['stockSymbol'] + 'sell'
            sell_trigger = cache.hgetall(key)

            if not sell_trigger:
                err = "Invalid cmd. User does not have a trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            
            else:
                # Add trigger point
                sell_trigger['triggerPrice'] = cmdDict['amount']
                cache.hmset(key, sell_trigger)
                
                # Decrease the number of stock shares in user's account 
                stock_key = cmdDict['user'] + sell_trigger['stockSymbol']
                user_stock = cache.hgetall(stock_key)

                user_stock['amount'] = float(user_stock['amount']) - (float(sell_trigger['amount']))
                cache.hmset(stock_key, user_stock)

                cmdDict['amount'] = float(sell_trigger['amount'])
                dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)
