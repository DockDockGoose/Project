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
            user_stock = list(Database.aggregate(ACCOUNTS_COLLECT, [
                    {'$match': {'_id': cmdDict['user'] }
                    }, {'$unwind': {'path': '$stocks'}
                    }, {'$match': {'stocks.stockSymbol': {'$eq': cmdDict['stockSymbol']}}
                    }, {'$limit': 1}
                ]))

            # Check if user has enough of stock in account
            if not user_stock:
                err = "Invalid cmd. User does not have the specified stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

            elif (user_stock[0]['stocks']['amount'] >= cmdDict['amount']):
                # Add sell command to user
                stock_data = {
                    'timestamp': time.time(),
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount'],
                    'price': stock_price
                }
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'sell': stock_data}})

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
            sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'sell': { '$exists': True } }, { 'sell': 1, '_id': 0})
            
            if(sell_cmd == None):
                err = "Invalid cmd. No recent pending buys" 
                dbLog.log(cmdDict, ERROR_LOG, err) 
            else: 
                # Check that less than 60s has passed
                sec_passed = time.time() - float(sell_cmd['sell']['timestamp'])
                if (sec_passed <= 60):
                    # Remove stocks from user and update funds
                    stock_data = {
                        'stockSymbol': sell_cmd['sell']['stockSymbol'],
                        'amount': sell_cmd['sell']['amount']
                    }
                    
                    # Decrease the amount of stock in user's account and increase user's fund
                    Database.update_one(ACCOUNTS_COLLECT, 
                        { '_id': cmdDict['user'], 'stocks.stockSymbol': sell_cmd['sell']['stockSymbol']},
                        {'$inc': { 'stocks.$.amount': -sell_cmd['sell']['amount'], 'funds': sell_cmd['sell']['amount'] * sell_cmd['sell']['price']}})

                    cmdDict['amount'] = sell_cmd['sell']['amount'] * sell_cmd['sell']['price']
                    dbLog.log(cmdDict, TRANSACT_LOG)
                else:
                    err = "Invalid cmd. More than 60 seconds passed." 
                    dbLog.log(cmdDict, ERROR_LOG, err) 

                #remove sell command   
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})

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
            sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'sell': { '$exists': True } }, { 'sell': 1, '_id': 0})

            if (sell_cmd == None):
                err = "Invalid cmd. No recent pending buys"
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Check that less than 60s has passed
                sec_passed = time.time() - sell_cmd['sell']['timestamp']
                if (sec_passed > 60):
                    err = "Invalid cmd. More than 60 seconds passed."
                    dbLog.log(cmdDict, ERROR_LOG, err)

                # Remove previous sell command
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)