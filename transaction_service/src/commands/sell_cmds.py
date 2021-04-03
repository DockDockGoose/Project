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


class SellCmd():
    def execute(cmdDict):
        """
            Sets up a sell command for the user and specified stock amount
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
            # Check for stock 
            stock_key = cmdDict['user'] + cmdDict['stockSymbol']
            user_stock = cache.hgetall(stock_key)

            # Check if user has enough of stock in account
            if not user_stock:
                err = "Invalid cmd. User does not have the specified stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

            elif float(user_stock['amount']) >= cmdDict['amount']:
                # Add sell command to user
                stock_data = {
                    'timestamp': time.time(),
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount'],
                    'price': stock_price
                }
                key = cmdDict['user'] + 'sell'
                cache.hmset(key, stock_data)
                cache.expire(key, TTL)

            else:
                err = "Invalid cmd. User has insufficient amount of stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)

class CommitSellCmd():
    def execute(cmdDict):
        """
            Executes the most recent sell command from the user
        """
        dbLog.log(cmdDict, CMD_LOG)
    
        try:
            # Check for previous sell command 
            key = cmdDict['user'] + 'sell'
            sell_cmd = cache.hgetall(key)

            if not sell_cmd:
                err = "Invalid cmd. No recent pending buys" 
                dbLog.log(cmdDict, ERROR_LOG, err) 
            else: 
                # Remove stocks from user and update funds
                stock_data = {
                    'stockSymbol': sell_cmd['stockSymbol'],
                    'amount': float(sell_cmd['amount'])
                }
                
                # Decrease the amount of stock in user's account
                stock_key = cmdDict['user'] + sell_cmd['stockSymbol']
                user_stock = cache.hgetall(stock_key)

                user_stock['amount'] = float(user_stock['amount']) - (float(sell_cmd['amount']) *  float(sell_cmd['price']))
                cache.hmset(stock_key, user_stock)
                
                # Increase user's fund
                account = cache.hgetall(cmdDict['user'])
                account['funds'] = float(account['funds']) + (float(sell_cmd['amount']) *  float(sell_cmd['price']))
                cache.hmset(cmdDict['user'], account)

                cmdDict['amount'] = float(sell_cmd['amount']) * float(sell_cmd['price'])
                dbLog.log(cmdDict, TRANSACT_LOG)

                #remove sell command   
                cache.hdel(*key)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)


class CancelSellCmd():
    def execute(cmdDict):
        """
            Cancels the most recent sell command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Get previous sell command 
            key = cmdDict['user'] + 'sell'
            sell_cmd = cache.hgetall(key)

            if not sell_cmd:
                err = "Invalid cmd. No recent pending buys"
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Remove previous sell command
                cache.hdel(*key)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)