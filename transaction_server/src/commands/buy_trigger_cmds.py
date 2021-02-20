import sys
import pymongo

from .db_log import dbLog

from database.database import Database

ACCOUNTS_COLLECT = "accounts"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'


class SetBuyAmtCmd():
    def execute(self, cmdDict):
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

                Database.insert(TRIGGER_COLLECT, buy_trigger)
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': -cmdDict['amount']}})

                dbLog.log(cmdDict, TRANSACT_LOG) 
            else:
                err = "Invalid cmd. User has insufficient funds." 
                dbLog.log(cmdDict, ERROR_LOG, err)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 

class CancelSetBuyCmd():
    def execute(self, cmdDict):
        """
            Cancels the set buy command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already set buy amount for the stock
            buy_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})

            if (buy_trigger == None):
                err = "Invalid cmd. User does not have a buy trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)

            else:
                # Add funds back to user's account and delete set_buy trigger
                Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': buy_trigger ['amount']}})
                Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})

                dbLog.log(cmdDict, TRANSACT_LOG)

        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err)

class SetBuyTriggerCmd():
    def execute(self, cmdDict):
        """
            Adds the price trigger to the set buy command
        """
        dbLog.log(cmdDict, CMD_LOG)

        try:
            # Check if person has already set buy amount for the stock
            buy_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})
            if  (buy_trigger == None):
                err = "Invalid cmd. User does not have a trigger for that stock." 
                dbLog.log(cmdDict, ERROR_LOG, err)
            else:
                # Add trigger point
                Database.update_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'}, {'$set': {'triggerPrice': cmdDict['amount']}})
                
        except pymongo.errors.PyMongoError as err:
            print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
            dbLog.log(cmdDict, ERROR_LOG, err) 

