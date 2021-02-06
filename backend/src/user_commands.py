""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
"""
""" TODO: 
        - finish all commandws
        - inferface with the SQL database. 
        - logging is out of order -> needs error checking
""" 

import time
import queue
import sys
sys.path.append('..')
from audit import logXML as log
from threading import Lock
cmd_print_lock = Lock()

buyAmtQ = queue.Queue()
sellAmtQ = queue.Queue()
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
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_CommitBuy(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)
    # The users account is modified after committing to buying the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))
    cmdDict['amount'] = buyAmtQ.get()
    buyAmtQ.task_done()
    cmdDict['command'] = REMOVE
    log.logEvents['accountTransaction'](cmdDict)

def CMD_CancelBuy(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_Sell(cmdDict):
    printCmd(cmdDict)
    sellAmtQ.put(cmdDict['amount'])
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)

def CMD_CommitSell(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
    log.logEvents['userCommand'](cmdDict)
    # The users account is modified after committing to sell the stock, log this action
    cmdDict['timestamp'] = str(int(time.time()))
    cmdDict['amount'] = sellAmtQ.get()
    sellAmtQ.task_done()
    cmdDict['command'] = ADD
    log.logEvents['accountTransaction'](cmdDict)

def CMD_CancelSell(cmdDict):
    printCmd(cmdDict)
    cmdDict['timestamp'] = str(int(time.time()))
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