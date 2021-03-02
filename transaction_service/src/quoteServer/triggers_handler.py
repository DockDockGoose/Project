"""
    Consistenly calls the quote server and triggers collection to execute any buy/sell triggers
"""
"""
    TODO:
        - add caching to limit amount of calls to quote server
        - be incorporated into transaction server or organize it so it can be run independently
"""
import time
import sys
import pymongo

from mockQuoteServer import MockQuoteServer
from quoteServer import QuoteServer

sys.path.append('../../../')
from database.src.database import Database
from database.src.db_log import dbLog


ACCOUNTS_COLLECT = "accounts"
TRIGGER_COLLECT = "triggers"

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
TRANSACT_LOG = 'accountTransaction'

def getQuote(cmdDict):
    """
        Retrieves price of stock for system triggers
            - does not contain the logging
    """

    try:
        # Create quote server (Note: this is the actual version for VM, use mock quote server for local testing by changing to MockQuoteServer instead)
        qs = MockQuoteServer()

        # query the quote server
        quote_data = qs.getQuote(cmdDict)

        # return the current price of shares
        return float(quote_data['price'])
    except:
        pass


def checkTriggers():
    """
        Get list of current triggers and execute any that meet the trigger price
    """

    cmds = list(Database.find(TRIGGER_COLLECT))

    if not cmds:
        return
    else:
        for cmd in cmds:

            # Check that trigger commands have both amount and price set
            if (cmd['triggerPrice'] == None or cmd['amount'] == None):
                cmds.remove(cmd)
            else:
                stock = cmd['stockSymbol']

                quote = {
                    'command': 'QUOTE',
                    'user': 'triggerHandler',
                    'stockSymbol': stock,
                    'timestamp': time.time()
                }

                # Get current price of stock
                price = getQuote(quote)

                # Check commands for specific stock
                for cmd in cmds:
                    if (cmd['stockSymbol'] == stock):

                        # Check if it meets the trigger price
                        if(price <= cmd['triggerPrice']):

                            if (cmd['type'] == 'buy'):
                                triggerBuyCmd(cmd, stock, price)

                            elif (cmd['type'] == 'sell'):
                                triggerSellCmd(cmd, stock, price)

                        # Remove cmd from list that don't meet trigger price to prevent rechecking
                        cmds.remove(cmd)

    return


def triggerBuyCmd(cmdDict, stock_symbol, price):
    """
        Buy the stock
    """

    cmdDict['timestamp'] = time.time()

    # Calculate the number of stock thee user gets
    stock_number = cmdDict['amount'] / price

    # Add the number of stocks to the user
    stock_data = {
        'stockSymbol': stock_symbol,
        'amount': stock_number
    }

    try:
        # Check if person already has stock
        stock_check = Database.find_one(ACCOUNTS_COLLECT,
                                        {'_id': cmdDict['user'], 'stocks.stockSymbol': stock_symbol})

        # Add new stock to user
        if (stock_check == None):
            Database.update_one(ACCOUNTS_COLLECT,
                                {'_id': cmdDict['user']},
                                {'$addToSet': {'stocks': stock_data}})
        else:
            # else increase their amount of stock
            Database.update_one(ACCOUNTS_COLLECT,
                                {'_id': cmdDict['user'], 'stocks.stockSymbol': stock_symbol},
                                {'$inc': {'stocks.$.amount': stock_number}})

        dbLog.log(cmdDict, TRANSACT_LOG)

        # Delete Buy trigger
        Database.remove(TRIGGER_COLLECT,
                        {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})

    except pymongo.errors.PyMongoError as err:
        print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
        dbLog.log(cmdDict, ERROR_LOG, err)


def triggerSellCmd(cmdDict, stock_symbol, price):
    """
        Sell the stock
    """
    cmdDict['timestamp'] = time.time()

    # Calculate the amount of money they gain from the sell
    stock_funds = cmdDict['amount'] * price

    try:
        # Increase user's fund
        Database.update_one(ACCOUNTS_COLLECT,
                            {'_id': cmdDict['user'], 'stocks.stockSymbol': stock_symbol},
                            {'$inc': {'funds': stock_funds}})

        dbLog.log(cmdDict, TRANSACT_LOG)

        # Delete Sell trigger
        Database.remove(TRIGGER_COLLECT,
                        {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})

    except pymongo.errors.PyMongoError as err:
        print(f"ERROR! Could not complete command {cmdDict['command']} failed with error: {err}")
        dbLog.log(cmdDict, ERROR_LOG, err)


if __name__ == '__main__':
    while True:
        checkTriggers()
        time.sleep(1)
