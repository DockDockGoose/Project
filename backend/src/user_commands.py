""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
"""
""" TODO: 
        - Extract commands into their own modules
        - sell/buy trigger checking of quote server
        - error handling
        - logging is out of order -> needs error checking
""" 

import time
import queue
import sys
import pymongo
sys.path.append('..')
from audit import logXML as log
from database import Database
from quoteServer import MockQuoteServer, QuoteServer


buyAmtQ = queue.Queue()
sellAmtQ = queue.Queue()
ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"
REMOVE = "REMOVE"
ADD = "ADD"

QUOTE_PORT       = 4444
QUOTE_HOST_NAME  = '192.168.4.2'

# Mock share price
# Delete later when quote command is working
current_share_price = 2

# Connect to database
Database.connect()
# Create quote server (Note: this is the actual version for VM, use mock quote server for local testing by changing to MockQuoteServer instead)
qs = QuoteServer()


def printCmd(cmdDict):
    """
        Prints out the current command being executed to the terminal
    """

    print("NUM, USER, CMD =  [{}, {}, {}]".format(cmdDict["transactionNumber"],
                                              cmdDict["user"],
                                              cmdDict["command"]))  

def cmdCompleted(cmdDict):
    """
        Keeps track of executed commands into transactions collection
    """
    print("-----",cmdDict["command"]," Command Executed-----")
    Database.insert(TRANSACT_COLLECT, cmdDict)

def CMD_Add(cmdDict, threadContext):
    """
        Adds money to user's account
    """
    printCmd(cmdDict)
    
    # Connect to database and check if user is new
    if (Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}) == None):
        # Modify command to get appropriate information for database
        user_data = {
            '_id': cmdDict['user'],
            'funds': float(cmdDict['amount'])
        }
        Database.insert(ACCOUNTS_COLLECT, user_data)
    else:
        # Get the user's current funds and add the new amount to it
        curr_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']},  { 'funds': 1, '_id': 0 })
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'funds': float(cmdDict['amount']) + curr_funds['funds']}})

    # We Add funds to account, timestamp this action then log UserCommand
    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))
    log.logEvents['userCommand'](cmdDict)

    # The users account is modified, log this action
    log.logEvents['accountTransaction'](cmdDict)

    cmdCompleted(cmdDict)

def CMD_Quote(cmdDict, threadContext):
    """
        Retrieves price of stock
    """
    printCmd(cmdDict)

    # query the quote server
    quote_data = qs.getQuote(cmdDict)
    print(quote_data)
    
    # Log the results from quote server
    cmdDict['price'] = quote_data['price']
    cmdDict['cryptokey'] = quote_data['cryptokey']
    cmdDict['timestamp'] = quote_data['timestamp']
    log.logEvents['quoteServer'](cmdDict)

    # Update the current price of shares
    current_share_price = float(quote_data['price'])

    cmdCompleted(cmdDict)

def CMD_Buy(cmdDict, threadContext):
    """
        Sets up a buy command for the user and specified stock
    """
    quoteCmd = {
        'command': 'QUOTE',
        'user': cmdDict['user'],
        'stockSymbol': cmdDict['stockSymbol'],
        'transactionNumber': cmdDict['transactionNumber'],
        'server': cmdDict['server']
    }

    CMD_Quote(quoteCmd, threadContext)

    printCmd(cmdDict)
    threadContext["buyAmtQ"].put(cmdDict['amount'])

    # Modify time in order to include seconds
    cmdDict['timestamp'] = time.time()

    # Make sure user has enough funds in account
    user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})
    if (user_funds['funds'] >= float(cmdDict['amount']) * current_share_price):
        # Add buy command to user
        stock_data = {
            'timestamp': cmdDict['timestamp'],
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'buy': stock_data}})

    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)

def CMD_CommitBuy(cmdDict, threadContext):
    """
        Executes the most recent buy command from user
    """
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()*1000))
    log.logEvents['userCommand'](cmdDict)

    # Check for previous buy command 
    buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'buy': { '$exists': True } }, { 'buy': 1, '_id': 0})
    print(buy_cmd)
    if (buy_cmd == None):
        cmdDict['amount'] = 0.00
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 
    else:
        # Check that less than 60s has passed
        sec_passed = time.time() - float(buy_cmd['buy']['timestamp'])
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
                {'$addToSet': { 'stocks': stock_data}, '$inc': {'funds': - buy_cmd['buy']['amount'] * current_share_price}})
            else:
                # else increase amount of stock
                final = Database.update_one(ACCOUNTS_COLLECT, 
                { '_id': cmdDict['user'], 'stocks.stockSymbol': buy_cmd['buy']['stockSymbol']},
                {'$inc': { 'stocks.$.amount': buy_cmd['buy']['amount'], 'funds': - buy_cmd['buy']['amount'] * current_share_price}})

        
        #remove buy command   
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})

    # The users account is modified after committing to buying the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()*1000))

    if not threadContext["buyAmtQ"].empty():
        threadContext["buyAmtQ"].put(cmdDict['amount'])
        log.logEvents['userCommand'](cmdDict)
    else: 
        cmdDict['amount'] = "0.00"
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 

    log.logEvents['accountTransaction'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelBuy(cmdDict, threadContext):
    """
        Cancels the most recent buy command from user
    """
    printCmd(cmdDict)

    # Get previous buy command 
    buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'buy': { '$exists': True } }, { 'buy': 1, '_id': 0})
    
    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['buy']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})
    
    cmdDict['timestamp'] = str(int(time.time()*1000))

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_Sell(cmdDict, threadContext):
    """
        Sets up a sell command for the user and specified stock amount
    """

    printCmd(cmdDict)
    threadContext["sellAmtQ"].put(cmdDict['amount'])

    quoteCmd = {
        'command': 'QUOTE',
        'user': cmdDict['user'],
        'stockSymbol': cmdDict['stockSymbol'],
        'transactionNumber': cmdDict['transactionNumber'],
        'server': cmdDict['server']
    }

    CMD_Quote(quoteCmd, threadContext)
    
    cmdDict['timestamp'] = str(time.time())

    #Make sure user has enough of stock in account
    user_stock = Database.aggregate(ACCOUNTS_COLLECT, [
            {'$match': {'_id': cmdDict['user'] }
            }, { '$unwind': {'path': '$stocks'}
            }, {'$match': {'stocks.stockSymbol': {'$eq': cmdDict['stockSymbol']}}
            }, {'$limit': 1}
        ])

    user_stock = list(user_stock)

    if (user_stock[0]['stocks']['amount'] >= cmdDict['amount']):
        # Add sell command to user
        stock_data = {
            'timestamp': cmdDict['timestamp'],
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'sell': stock_data}})

    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CommitSell(cmdDict, threadContext):
    """
        Executes the most recent sell command from the user
    """
    printCmd(cmdDict)

    # Check for previous sell command 
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'sell': { '$exists': True } }, { 'sell': 1, '_id': 0})
    
    if(sell_cmd == None):
        cmdDict['amount'] = 0.00
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 
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
                {'$inc': { 'stocks.$.amount': -sell_cmd['sell']['amount'], 'funds': sell_cmd['sell']['amount'] * current_share_price}})
        
        #remove sell command   
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})
        cmdDict['amount'] = sell_cmd['sell']['amount']

    # The users account is modified after committing to sell the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()*1000))

    if not threadContext["sellAmtQ"].empty():
        threadContext["sellAmtQ"].put(cmdDict['amount'])
        log.logEvents['userCommand'](cmdDict)
    else: 
        cmdDict['amount'] = "0.00"
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 

    log.logEvents['accountTransaction'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelSell(cmdDict, threadContext):
    """
        Cancels the most recent sell command
    """
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()*1000))

    # Get previous sell command 
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user'], 'sell': { '$exists': True } }, { 'sell': 1, '_id': 0})

    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['sell']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_SetBuyAmt(cmdDict, threadContext):
    """
        Creates a buy trigger based on the number of the stocks the user wants to buy
    """
    printCmd(cmdDict)

    # Check user has enough funds in account
    user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})
    if (user_funds['funds'] >= float(cmdDict['amount'])):
        # Add new trigger buy command and remove funds from user account
        buy_trigger = {
            'user': cmdDict['user'],
            'type': 'buy',
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.insert(TRIGGER_COLLECT, buy_trigger)
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': -cmdDict['amount']}})

        cmdDict['timestamp'] = str(int(time.time()*1000))
        cmdDict['amount'] = str(int(cmdDict['amount']))
        log.logEvents['userCommand'](cmdDict)
    else:
        cmdDict['timestamp'] = str(int(time.time()*1000))
        cmdDict['amount'] = str(int(cmdDict['amount']))
        cmdDict['errorMessage'] = "Insufficient funds. Cannot set buy amount." 

        log.logEvents['errorEvent'](cmdDict)
    
    cmdCompleted(cmdDict)

def CMD_CancelSetBuy(cmdDict, threadContext):
    """
        Cancels the set buy command
    """
    printCmd(cmdDict)

    # Check if person has already set buy amount for the stock
    buy_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})
    if  (buy_trigger != None):
        # Add funds back to user's account and delete set_buy trigger
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': buy_trigger ['amount']}})
        Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})
    
    cmdDict['timestamp'] = str(int(time.time()*1000))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)
    
def CMD_SetBuyTrigger(cmdDict, threadContext):
    """
        Adds the price trigger to the set buy command
    """

    printCmd(cmdDict)

    # Check if person has already set buy amount for the stock
    if  (Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'}) != None):
        # Add trigger point
        Database.update_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'}, {'$set': {'triggerPrice': cmdDict['amount']}})

    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)

def CMD_SetSellAmt(cmdDict, threadContext):
    """
        Creates a sell trigger based on the number of stocks the user wants to sell
    """
    
    printCmd(cmdDict)

    # Get amount of stock from user
    user_stock = Database.aggregate(ACCOUNTS_COLLECT, [
            {'$match': {'_id': cmdDict['user'] }
            }, { '$unwind': {'path': '$stocks'}
            }, {'$match': {'stocks.stockSymbol': {'$eq': cmdDict['stockSymbol']}}
            }, {'$limit': 1}
        ])

    user_stock = list(user_stock)

    # Check if user has enough of stock in account and initialize sell trigger
    if (user_stock[0]['stocks']['amount'] >= cmdDict['amount']):
        sell_trigger = {
            'user': cmdDict['user'],
            'type': 'sell',
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.insert(TRIGGER_COLLECT, sell_trigger)

    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelSetSell(cmdDict, threadContext):
    """
        Cancels the set sell command
    """
    printCmd(cmdDict)

    # Check if person has already set sell amount for the stock
    sell_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
    if  (sell_trigger != None):
        # Add number of stuck back to user's account and delete set_sell trigger
        Database.update_one(ACCOUNTS_COLLECT, 
        { '_id': cmdDict['user'], 'stocks.stockSymbol': cmdDict['stockSymbol']},
        {'$inc': { 'stocks.$.amount': sell_trigger['amount']}})

        Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
    
    cmdDict['timestamp'] = str(int(time.time()*1000))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)


def CMD_SetSellTrigger(cmdDict, threadContext):
    """
        Adds the price trigger to the set sell command
    """
    printCmd(cmdDict)

    # Check if person has already has set sell amount for the stock
    sell_amt_cmd = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
    if ( sell_amt_cmd != None):
        # Add trigger point
        Database.update_one(TRIGGER_COLLECT,
        {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'},
        {'$set': {'triggerPrice': cmdDict['amount']}})
        
        # Decrease the number of stock shares in user's account 
        Database.update_one(ACCOUNTS_COLLECT, 
        { '_id': cmdDict['user'], 'stocks.stockSymbol': sell_amt_cmd['stockSymbol']},
        {'$inc': { 'stocks.$.amount': - sell_amt_cmd['amount']}})

    cmdDict['timestamp'] = str(int(time.time()*1000))
    cmdDict['amount'] = str(int(cmdDict['amount']))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)


def CMD_Dumplog(cmdDict, threadContext):
    """
        Print all of the transactions or just the user's transactions
    """
    
    printCmd(cmdDict)

    # Get entire log or use log
    if 'user' in cmdDict.keys():
        transactions = list(Database.find(TRANSACT_COLLECT, {'user': cmdDict['user']}))
    else:
        transactions = list(Database.find(TRANSACT_COLLECT))

    try:
        with open(cmdDict['filename'], 'w') as f:
            for transact in transactions:
                f.write("%s\n" % transact)
    except IOError:
        print("Error while trying to open and write to", cmdDict['filename'])
        
    f.close()
    cmdDict['timestamp'] = str(int(time.time()*1000))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)


def CMD_DisplaySummary(cmdDict, threadContext):
    """
        Print the user's account from accounts, transaction history, and buy/sell triggers
    """
    printCmd(cmdDict)
    
    user_transactions = list(Database.find(TRANSACT_COLLECT, {'user': cmdDict['user']}))

    user_account = list(Database.find(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}))

    user_triggers = list(Database.find(TRIGGER_COLLECT, {'user': cmdDict['user']}))

    print("----- User's Transaction History -----\n", user_transactions)
    print("\n----- User's Current Account Status -----\n", user_account)
    print("\n----- User's Triggers -----\n", user_triggers)

    cmdDict['timestamp'] = str(int(time.time()*1000))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)

userCommands = {
    'ADD'               : CMD_Add,
    'QUOTE'             : CMD_Quote,
    'BUY'               : CMD_Buy,
    'COMMIT_BUY'        : CMD_CommitBuy,
    'CANCEL_BUY'        : CMD_CancelBuy,
    'SELL'              : CMD_Sell,
    'COMMIT_SELL'       : CMD_CommitSell,
    'CANCEL_SELL'       : CMD_CancelSell,
    'SET_BUY_AMOUNT'    : CMD_SetBuyAmt,
    'CANCEL_SET_BUY'    : CMD_CancelSetBuy,
    'SET_BUY_TRIGGER'   : CMD_SetBuyTrigger,
    'SET_SELL_AMOUNT'   : CMD_SetSellAmt,
    'CANCEL_SET_SELL'   : CMD_CancelSetSell,
    'SET_SELL_TRIGGER'  : CMD_SetSellTrigger,
    'DUMPLOG'           : CMD_Dumplog,
    'DISPLAY_SUMMARY'   : CMD_DisplaySummary,
}

