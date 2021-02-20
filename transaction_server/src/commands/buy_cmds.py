import sys
import time
import pymongo

from .db_log import dbLog
from .quote_cmd import QuoteCmd

from ..database.database import Database



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

        stock_price = QuoteCmd.CMD_Quote(quote)

        try:
            # Make sure user exist and has enough funds in account
            user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})

            if (user_funds == None):
                err = "Invalid cmd. User does not exist." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

            elif (user_funds['funds'] >= cmdDict['amount'] * stock_price):
                # Add buy command to user
                stock_data = {
                    'timestamp': time.time(),
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount'],
                    'price': stock_price
                }
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'buy': stock_data}})
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
            buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'buy': { '$exists': True } }, { 'buy': 1, '_id': 0})
            
            if (buy_cmd == None):
                err = "Invalid cmd. No recent pending buys" 
                dbLog.log(cmdDict, ERROR_LOG, err) 
            else:
                # Check that less than 60s has passed
                sec_passed = time.time() - buy_cmd['buy']['timestamp']
                if (sec_passed <= 60):
                
                    # Add stocks to user and update funds
                    stock_data = {
                        'stockSymbol': buy_cmd['buy']['stockSymbol'],
                        'amount': buy_cmd['buy']['amount']
                    }
                    # Check if person already has stock
                    stock_check = Database.find_one(ACCOUNTS_COLLECT, { '_id': cmdDict['user'], 'stocks.stockSymbol': buy_cmd['buy']['stockSymbol']})
                            
                    if (stock_check == None):
                        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, 
                        {'$addToSet': { 'stocks': stock_data}, '$inc': {'funds': - buy_cmd['buy']['amount'] * buy_cmd['buy']['price']}})
                    else:
                        # else increase their amount of stock
                        final = Database.update_one(ACCOUNTS_COLLECT, 
                        { '_id': cmdDict['user'], 'stocks.stockSymbol': buy_cmd['buy']['stockSymbol']},
                        {'$inc': { 'stocks.$.amount': buy_cmd['buy']['amount'], 'funds': - buy_cmd['buy']['amount'] * buy_cmd['buy']['price']}})

                    dbLog.log(cmdDict, TRANSACT_LOG)

                else:
                    err = "Invalid cmd. More than 60 seconds passed." 
                    dbLog.log(cmdDict, ERROR_LOG, err) 

                #remove buy command   
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})

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
            buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'buy': { '$exists': True } }, { 'buy': 1, '_id': 0})
            
            if (buy_cmd == None):
                err = "Invalid cmd. No recent pending buys." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            
            else: # Check that less than 60s has passed
                sec_passed = time.time() - buy_cmd['buy']['timestamp']
                if (sec_passed > 60):
                    err = "Invalid cmd. More than 60 seconds passed." 
                    dbLog.log(cmdDict, ERROR_LOG, err)

                # Remove previous buy command
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})
                dbLog.log(cmdDict, TRANSACT_LOG) 

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 
