""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
"""
""" TODO: 
        - finish all commands
        - inferface with the SQL database. 
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
TRIGGERS_COLLECT = "triggers"
REMOVE = "REMOVE"
ADD = "ADD"

def printCmd(cmdDict):
    with cmd_print_lock:
        command = cmdDict["command"]
        print("PACKET CONTENTS:", cmdDict)
        print("    Trans. #: ",   cmdDict["transactionNumber"])
        print("    CMD:      ",   command)

def CMD_Add(cmdDict):
    printCmd(cmdDict)
    
    # Modify time in order to include seconds
    cmdDict['timestamp'] = str(time.time())
    
    # Connect to database and check if user is new
    Database.connect()
    if (Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}) == None):
        # Modify command to get appropriate information for database
        user_data = {
            '_id': cmdDict['user'],
            'funds': float(cmdDict['amount'])
        }
        print(user_data)
        Database.insert(ACCOUNTS_COLLECT, user_data)
    else:
        # Get the user's current funds and add the new amount to it
        curr_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']},  { 'funds': 1, '_id': 0 })
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'funds': float(cmdDict['amount']) + curr_funds['funds']}})
    
    # Add command to transaction collection
    Database.insert(TRANSACT_COLLECT, cmdDict)

    # We Add funds to account, timestamp this action then log UserCommand
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # The users account is modified, log this action
    log.logEvents['accountTransaction'](cmdDict)

def CMD_Quote(cmdDict):
    printCmd(cmdDict)
    # query the legacy quoteserver -> should return price of the stock
    mockPrice = "10.00"
    mockCryptoKey = "IRrR7UeTO35kSWUgG0QJKmB35sL27FKM7AVhP5qpjCgmWQeXFJs35g"
    cmdDict['price'] = mockPrice
    cmdDict['cryptokey'] = mockCryptoKey
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['quoteServer'](cmdDict)

def CMD_Buy(cmdDict):
    printCmd(cmdDict)
    buyAmtQ.put(cmdDict['amount'])

    # Modify time in order to include seconds
    cmdDict['timestamp'] = str(time.time())

    # Connect to database and make sure user has enough funds in account
    Database.connect()
    user_funds = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'funds': 1, '_id': 0})
    if (user_funds['funds'] >= float(cmdDict['amount'])):
        # Add buy command to user
        stock_data = {
            'timestamp': cmdDict['timestamp'],
            'stockSymbol': cmdDict['stockSymbol'],
            'amount': cmdDict['amount']
        }
        Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$set': { 'buy': stock_data}})
    # Add buy command to transaction collection
    Database.insert(TRANSACT_COLLECT, cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_CommitBuy(cmdDict):
    printCmd(cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # Connect to database and get previous buy command 
    Database.connect()
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
            Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$addToSet': { 'stocks': stock_data}, '$inc': {'funds': -buy_cmd['buy']['amount']}})
        else:
            # else increase amount of stock
            final = Database.update_one(ACCOUNTS_COLLECT, 
            { '_id': cmdDict['user'], 'stocks.stockSymbol': buy_cmd['buy']['stockSymbol']},
            {'$inc': { 'stocks.$.amount': buy_cmd['buy']['amount'], 'funds': -buy_cmd['buy']['amount']}})

    
    #remove buy command   
    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})
    Database.insert(TRANSACT_COLLECT, cmdDict)

    # The users account is modified after committing to buying the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))
    cmdDict['amount'] = buyAmtQ.get()
    buyAmtQ.task_done()
    cmdDict['command'] = REMOVE
    log.logEvents['accountTransaction'](cmdDict)

def CMD_CancelBuy(cmdDict):
    printCmd(cmdDict)

    # Connect to database and get previous buy command 
    Database.connect()
    buy_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'buy': 1, '_id': 0})
    
    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['buy']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'buy': ""}})
    Database.insert(TRANSACT_COLLECT, cmdDict)
    
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_Sell(cmdDict):
    printCmd(cmdDict)
    sellAmtQ.put(cmdDict['amount'])

    cmdDict['timestamp'] = str(time.time())

    # Connect to database and make sure user has enough of stock in account
    Database.connect()
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
    # Add buy command to transaction collection
    Database.insert(TRANSACT_COLLECT, cmdDict)

    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_CommitSell(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

    # Connect to database and get previous sell command 
    Database.connect()
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'sell': 1, '_id': 0})
    
    # Check that less than 60s has passed
    sec_passed = time.time() - float(sell_cmd['sell']['timestamp'])
    if (sec_passed <= 60):
         # Add stocks to user and update funds
        stock_data = {
            'stockSymbol': sell_cmd['sell']['stockSymbol'],
            'amount': sell_cmd['sell']['amount']
        }
        
        # Decrease the amount of stock in user's account and increase user's fund
        Database.update_one(ACCOUNTS_COLLECT, 
            { '_id': cmdDict['user'], 'stocks.stockSymbol': sell_cmd['sell']['stockSymbol']},
            {'$inc': { 'stocks.$.amount': -sell_cmd['sell']['amount'], 'funds': float(sell_cmd['sell']['amount'])}})
    
    #remove sell command   
    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})
    Database.insert(TRANSACT_COLLECT, cmdDict)

    # The users account is modified after committing to sell the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))
    cmdDict['amount'] = sellAmtQ.get()
    sellAmtQ.task_done()
    cmdDict['command'] = ADD
    log.logEvents['accountTransaction'](cmdDict)

def CMD_CancelSell(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))

    # Connect to database and get previous sell command 
    Database.connect()
    sell_cmd = Database.find_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, { 'sell': 1, '_id': 0})

    # Not sure if to include this because it would be cancelled either way
    # Check that less than 60s has passed
    # sec_passed = time.time() - float(buy_cmd['sell']['timestamp'])
    # if (sec_passed <= 60):

    Database.update_one(ACCOUNTS_COLLECT, {'_id': cmdDict['user']}, {'$unset': { 'sell': ""}})
    Database.insert(TRANSACT_COLLECT, cmdDict)


    log.logEvents['userCommand'](cmdDict)

def CMD_SetBuyAmt(cmdDict):
    printCmd(cmdDict)
    try:
        cmdDict['timestamp'] = str(int(time.time()))
        log.logEvents['userCommand'](cmdDict)
    except:
        cmdDict['timestamp'] = str(int(time.time()))
        cmdDict['errorMessage'] = "Insufficient funds. Cannot set buy amount." 
        log.logEvents['errorEvent'](cmdDict)

def CMD_CancelSetBuy(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_SetBuyTrigger(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_SetSellAmt(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_CancelSetSell(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_SetSellTrigger(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_Dumplog(cmdDict):
    printCmd(cmdDict)

def CMD_DisplaySummary(cmdDict):
    printCmd(cmdDict)

add_test_data = {
    'pid': 123,
    'transactionNumber': 1,
    'command': 'ADD',
    'user': 'oY01WVirLr',
    'amount': 63511.53
}

#CMD_Add(add_test_data)

buy_test_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'BUY',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
    'amount': 100
}

#CMD_Buy(buy_test_data)


buy_commit_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'COMMIT_BUY',
    'user': 'oY01WVirLr'
}

#CMD_CommitBuy(buy_commit_data)

buy_cancel_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'CANCEL_BUY',
    'user': 'oY01WVirLr'
}

#CMD_CancelBuy(buy_cancel_data)

sell_test_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'SELL',
    'user': 'oY01WVirLr',
    'stockSymbol': 'B',
    'amount': 1
}

#CMD_Sell(sell_test_data)


sell_commit_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'COMMIT_SELL',
    'user': 'oY01WVirLr'
}

#CMD_CommitSell(sell_commit_data)

sell_cancel_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'CANCEL_SELL',
    'user': 'oY01WVirLr'
}

#CMD_CancelSell(sell_cancel_data)


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


buyAmtQ.join()
sellAmtQ.join()