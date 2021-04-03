import sys
import time
import pymongo
import redis

from .quote_cmd import QuoteCmd

sys.path.append('../../')

from database.src.database import Database
from database.src.db_log import dbLog

cache = redis.StrictRedis(charset="utf-8", decode_responses=True, host='localhost', port=6379, password='dockdockgoose')
TTL = 60

ACCOUNTS_COLLECT = "accounts"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'

class BuyCmd():
    def execute(cmdDict):
        """
            Sets up a buy command for the user and specified stock
        """
        dbLog.log(cmdDict, CMD_LOG) 

        quote = {
            'command': 'QUOTE',
            'user': cmdDict['user'],
            'stockSymbol': cmdDict['stockSymbol'],
            'transactionNumber': cmdDict['transactionNumber'],
            'server': cmdDict['server']
        }

        stock_price = QuoteCmd.execute(quote)

        try:
            # Make sure user exist and has enough funds in account
            user_funds = float(cache.hget(cmdDict['user'], 'funds'))

            if user_funds == None:
                err = "Invalid cmd. User does not exist." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

            elif (user_funds >= cmdDict['amount'] * stock_price):
                # Add buy command to user
                stock_data = {
                    'timestamp': time.time(),
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount'],
                    'price': stock_price
                }

                key = cmdDict['user'] + 'buy'
                cache.hmset(key, stock_data)
                cache.expire(key, TTL)
                dbLog.log(cmdDict, TRANSACT_LOG) 

            else:
                err = "Invalid cmd. User has insufficient funds." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 

class CommitBuyCmd:
    def execute(cmdDict):
        """
            Executes the most recent buy command from user
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Get previous buy command 
            buy_key = cmdDict['user'] + 'buy'
            buy_cmd = cache.hgetall(buy_key)
            
            if not buy_cmd:
                err = "Invalid cmd. No recent pending buys" 
                dbLog.log(cmdDict, ERROR_LOG, err) 
            else:                
                # Check if person already has stock
                stock_key = cmdDict['user'] + buy_cmd['stockSymbol']
                user_stock = cache.hgetall(stock_key)

                if not user_stock:
                    # add new stock
                    user_stock = {
                        'stockSymbol': buy_cmd['stockSymbol'],
                        'amount': float(buy_cmd['amount'])
                    }
                    cache.hmset(stock_key, user_stock)
                else:
                    # else increase their amount of stock
                    user_stock['amount'] = float(buy_cmd['amount']) + float(user_stock['amount'])
                    cache.hmset(stock_key, user_stock)
                           
                # Decrease user's funds
                account = cache.hgetall(cmdDict['user'])
                account['funds'] = float(account['funds']) - (float(buy_cmd['amount']) *  float(buy_cmd['price']))
                cache.hmset(cmdDict['user'], account)

                cmdDict['amount'] = float(buy_cmd['amount']) *  float(buy_cmd['price'])
                dbLog.log(cmdDict, TRANSACT_LOG)

                #remove buy command
                cache.hdel(*buy_key)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 


class CancelBuyCmd:
    def execute(cmdDict):
        """
            Cancels the most recent buy command from user
        """
        dbLog.log(cmdDict, CMD_LOG)

        try: 
            # Get previous buy command 
            key = cmdDict['user'] + 'buy'
            buy_cmd = cache.hgetall(key)

            if not buy_cmd:
                err = "Invalid cmd. No recent pending buys." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            
            else:
                # Remove previous buy command
                cache.hdel(*key)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 
