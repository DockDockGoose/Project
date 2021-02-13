""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
"""
""" TODO: 
        - finish all commands
        - inferface with the SQL database. 
        - error handling
        - logging is out of order -> needs error checking
""" 

import time
import queue
import sys
import pymongo
sys.path.append('..')
from audit import logXML as log
from threading import Lock
from database import Database
cmd_print_lock = Lock()

buyAmtQ = queue.Queue()
sellAmtQ = queue.Queue()
ACCOUNTS_COLLECT = "accounts"
TRANSACT_COLLECT = "transactions"
TRIGGER_COLLECT = "triggers"
REMOVE = "REMOVE"
ADD = "ADD"

# Mock share price
# Delete later when quote command is working
mock_share_price = 2

# Connect to database
Database.connect()

def printCmd(cmdDict):
    with cmd_print_lock:
        command = cmdDict["command"]
        print("PACKET CONTENTS:", cmdDict)
        print("    Trans. #: ",   cmdDict["transactionNumber"])
        print("    CMD:      ",   command)

def cmdCompleted(cmdDict, threadContext):
    print("-----",cmdDict["command"]," Command Executed-----")
    Database.insert(TRANSACT_COLLECT, cmdDict)

def CMD_Add(cmdDict):
    printCmd(cmdDict)
    
    # Modify time in order to include seconds
    cmdDict['timestamp'] = time.time()
    
    # Connect to database and check if user is new
    if (Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}) == None):
        # Modify command to get appropriate information for database
        user_data = {
            '_id': cmdDict['user'],
            'funds': float(cmdDict['amount'])
        }
        Database.insert(TRANSACT_COLLECT, user_data)
    else:
        # Get the user's current funds and add the new amount to it
        curr_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']},  { 'funds': 1, '_id': 0 })
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'funds': float(cmdDict['amount']) + curr_funds['funds']}})
    
    cmdCompleted(cmdDict)

    # We Add funds to account, timestamp this action then log UserCommand
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # The users account is modified, log this action
    log.logEvents['accountTransaction'](cmdDict)

def CMD_Quote(cmdDict, threadContext):
    printCmd(cmdDict)

    # query the legacy quoteserver -> should return price of the stock
    mockPrice = "10.00"
    mockCryptoKey = "IRrR7UeTO35kSWUgG0QJKmB35sL27FKM7AVhP5qpjCgmWQeXFJs35g"
    cmdDict['price'] = mockPrice
    cmdDict['cryptokey'] = mockCryptoKey
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['quoteServer'](cmdDict)

def CMD_Buy(cmdDict, threadContext):
    printCmd(cmdDict)
    buyAmtQ.put(cmdDict['amount'])

    # Modify time in order to include seconds
    cmdDict['timestamp'] = time.time()

    # Make sure user has enough funds in account
    user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})
    if (user_funds['funds'] >= float(cmdDict['amount']) * mock_share_price):
        # Add buy command to user
        stock_data = {
            'timestamp': cmdDict['timestamp'],
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'buy': stock_data}})

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)

def CMD_CommitBuy(cmdDict, threadContext):
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # Get previous buy command 
    buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'buy': 1, '_id': 0})
    
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
            {'$addToSet': { 'stocks': stock_data}, '$inc': {'funds': -buy_cmd['buy']['amount'] * mock_share_price}})
        else:
            # else increase amount of stock
            final = Database.update_one(ACCOUNTS_COLLECT, 
            { '_id': cmdDict['user'], 'stocks.stockSymbol': buy_cmd['buy']['stockSymbol']},
            {'$inc': { 'stocks.$.amount': buy_cmd['buy']['amount'], 'funds': -buy_cmd['buy']['amount']} * mock_share_price})

    
    #remove buy command   
    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})

    # The users account is modified after committing to buying the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))

    if not threadContext["buyAmtQ"].empty():
        threadContext["buyAmtQ"].put(cmdDict['amount'])
        cmdDict['timestamp'] = str(int(time.time()))
        log.logEvents['userCommand'](cmdDict)
    else: 
        cmdDict['amount'] = 0.00
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 

    log.logEvents['accountTransaction'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelBuy(cmdDict, threadContext):
    printCmd(cmdDict)

    # Get previous buy command 
    buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'buy': 1, '_id': 0})
    
    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['buy']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})
    
    cmdDict['timestamp'] = str(int(time.time()))

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_Sell(cmdDict, threadContext):
    printCmd(cmdDict)
    sellAmtQ.put(cmdDict['amount'])

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

    cmdDict['timestamp'] = str(int(time.time()))

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CommitSell(cmdDict, threadContext):
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # Get previous sell command 
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'sell': 1, '_id': 0})
    
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
            {'$inc': { 'stocks.$.amount': -sell_cmd['sell']['amount'], 'funds': float(sell_cmd['sell']['amount']) * mock_share_price}})
    
    #remove sell command   
    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})

    # The users account is modified after committing to sell the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))

    if not threadContext["sellAmtQ"].empty():
        cmdDict['amount'] = threadContext["sellAmtQ"].get()
        
        threadContext["sellAmtQ"].task_done()
    else:
        cmdDict['amount'] = 0.00
        cmdDict['errorMessage'] = "Invalid cmd. No recent pending buys" 

    cmdDict['command'] = ADD
    log.logEvents['accountTransaction'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelSell(cmdDict, threadContext):
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))

    # Get previous sell command 
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'sell': 1, '_id': 0})

    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['sell']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})

    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_SetBuyAmt(cmdDict, threadContext):
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
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': -cmdDict['amount'] * mock_share_price}})

        cmdDict['timestamp'] = str(int(time.time()))
        log.logEvents['userCommand'](cmdDict)
    else:
        cmdDict['timestamp'] = str(int(time.time()))
        cmdDict['errorMessage'] = "Insufficient funds. Cannot set buy amount." 

        log.logEvents['errorEvent'](cmdDict)
    
    cmdCompleted(cmdDict)

def CMD_CancelSetBuy(cmdDict, threadContext):
    printCmd(cmdDict)

    # Check if person has already set buy amount for the stock
    buy_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})
    if  (buy_trigger != None):
        # Add funds back to user's account and delete set_buy trigger
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$inc': {'funds': buy_trigger ['amount']}})
        Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'})
    
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_SetBuyTrigger(cmdDict, threadContext):
    printCmd(cmdDict)

    # Check if person has already set buy amount for the stock
    if  (Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'}) != None):
        # Add trigger point
        Database.update_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'buy'}, {'$set': {'triggerPrice': cmdDict['amount']}})

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_SetSellAmt(cmdDict, threadContext):
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

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    cmdCompleted(cmdDict)


def CMD_CancelSetSell(cmdDict, threadContext):
    printCmd(cmdDict)

    # Check if person has already set sell amount for the stock
    sell_trigger = Database.find_one(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
    if  (sell_trigger != None):
        # Add number of stuck back to user's account and delete set_sell trigger
        Database.update_one(ACCOUNTS_COLLECT, 
        { '_id': cmdDict['user'], 'stocks.stockSymbol': cmdDict['stockSymbol']},
        {'$inc': { 'stocks.$.amount': sell_trigger['amount']}})

        Database.remove(TRIGGER_COLLECT, {'user': cmdDict['user'], 'stockSymbol': cmdDict['stockSymbol'], 'type': 'sell'})
    
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)


def CMD_SetSellTrigger(cmdDict, threadContext):
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


    Database.insert(TRANSACT_COLLECT, cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)
    cmdCompleted(cmdDict)


def CMD_Dumplog(cmdDict, threadContext):
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
    cmdCompleted(cmdDict)


def CMD_DisplaySummary(cmdDict, threadContext):
    printCmd(cmdDict)
    # Print the user's account from accounts, transaction history, and buy/sell triggers
    user_transactions = list(Database.find(TRANSACT_COLLECT, {'user': cmdDict['user']}))

    user_account = list(Database.find(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}))

    user_triggers = list(Database.find(TRIGGER_COLLECT, {'user': cmdDict['user']}))

    print("----- User's Transaction History -----\n", user_transactions)
    print("\n----- User's Current Account Status -----\n", user_account)
    print("\n----- User's Triggers -----\n", user_triggers)

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

