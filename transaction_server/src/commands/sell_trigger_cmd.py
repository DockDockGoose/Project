import sys

import pymongo

from .db_log import dbLog

from ..database.database import Database


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
            user_stock = list(Database.aggregate(ACCOUNTS_COLLECT, [
                    {'$match': {'_id': cmdDict['user'] }
                    }, { '$unwind': {'path': '$stocks'}
                    }, {'$match': {'stocks.stockSymbol': {'$eq': cmdDict['stockSymbol']}}
                    }, {'$limit': 1}
                ]))

            if (user_stock[0] == None):
                err = "Invalid cmd. User does not have the specified stock." 
                dbLog.log(cmdDict, ERROR_LOG, err) 

            # Check if user has enough of stock in account and initialize sell trigger
            elif (user_stock[0]['stocks']['amount'] >= cmdDict['amount']):
                sell_trigger = {
                    'user': cmdDict['user'],
                    'type': 'sell',
                    'stockSymbol': cmdDict['stockSymbol'],
                    'amount': cmdDict['amount']
                }
                Database.insert(TRIGGER_COLLECT, sell_trigger)

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
            sell_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})

            if (sell_trigger == None):
                err = "Invalid cmd. User does not have a sell trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Re-add funds only if trigger price had been set
                if (sell_trigger['triggerPrice'] != None):
                    Database.update_one(ACCOUNTS_COLLECT,
                        { '_id': cmdDict['user'], 'stocks.stockSymbol': cmdDict['stockSymbol']},
                        {'$inc': { 'stocks.$.amount': sell_trigger['amount']}}
                    )
                    dbLog.log(cmdDict, TRANSACT_LOG)
                # Delete sell trigger
                Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})

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
            sell_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
            
            if(sell_trigger == None):
                err = "Invalid cmd. User does not have a trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            
            else:
                # Add trigger point
                Database.update_one(TRIGGER_COLLECT,
                    {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'},
                    {'$set': {'triggerPrice': cmdDict['amount']}}
                )
                
                # Decrease the number of stock shares in user's account 
                Database.update_one(ACCOUNTS_COLLECT, 
                    { '_id': cmdDict['user'], 'stocks.stockSymbol': sell_trigger['stockSymbol']},
                    {'$inc': { 'stocks.$.amount': - sell_trigger['amount']}}
                )
                
                dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)
