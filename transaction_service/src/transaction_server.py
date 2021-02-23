""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
"""
"""
    TODO:
        - change to server to communicate with web server
        - add call to trigger handler 
"""

import socket
import sys
import time
import ast
import queue

from .commands.add_cmd import AddCmd
from .commands.quote_cmd import QuoteCmd
from .commands.buy_cmds import BuyCmd, CommitBuyCmd, CancelBuyCmd
from .commands.buy_trigger_cmds import SetBuyAmtCmd, SetBuyTriggerCmd, CancelSetBuyCmd
from .commands.sell_cmds import SellCmd, CommitSellCmd, CancelSellCmd
from .commands.sell_trigger_cmd import SetSellAmtCmd, SetSellTriggerCmd, CancelSetSellCmd
from .commands.display_sum_cmd import DisplaySumCmd
from .commands.dumplog_cmd import DumplogCmd

sys.path.append('../../')
from database.src.database import Database

# Connect to database
Database.connect()

def printCmd(cmdDict):
    """
        Prints out the current command being executed to the terminal
    """
    print("NUM, USER, CMD =  [{}, {}, {}]".format(cmdDict["transactionNumber"],
                                                  cmdDict["user"],
                                                  cmdDict["command"]))  

def cmdCompleted(cmdDict, startTime):
    """
        Keeps track of executed commands into transactions collection
    """
    elapsedTime = time.time() - startTime

    print("-----[{}, {}, {}s] Command Executed".format(cmdDict["transactionNumber"],
                                                    cmdDict["command"],
                                                    round(elapsedTime, 3)))

def CMD_Add(cmdDict, threadContext, startTime):
    """
        Adds money to user's account
    """
    printCmd(cmdDict)
    AddCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_Quote(cmdDict, threadContext, startTime):
    """
        Retrieves price of stock
    """
    printCmd(cmdDict)
    QuoteCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_Buy(cmdDict, threadContext, startTime):
    """
        Sets up a buy command for the user and specified stock
    """
    printCmd(cmdDict)
    BuyCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_CommitBuy(cmdDict, threadContext, startTime):
    """
        Executes the most recent buy command from user
    """
    printCmd(cmdDict)
    CommitBuyCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_CancelBuy(cmdDict, threadContext, startTime):
    """
        Cancels the most recent buy command from user
    """
    printCmd(cmdDict)
    CancelBuyCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_Sell(cmdDict, threadContext, startTime):
    """
        Sets up a sell command for the user and specified stock amount
    """
    printCmd(cmdDict)
    SellCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_CommitSell(cmdDict, threadContext, startTime):
    """
        Executes the most recent sell command from the user
    """
    printCmd(cmdDict)
    CommitSellCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_CancelSell(cmdDict, threadContext, startTime):
    """
        Cancels the most recent sell command
    """
    printCmd(cmdDict)
    CancelSellCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_SetBuyAmt(cmdDict, threadContext, startTime):
    """
        Creates a buy trigger based on the number of the stocks the user wants to buy
    """
    printCmd(cmdDict)
    SetBuyAmtCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_CancelSetBuy(cmdDict, threadContext, startTime):
    """
        Cancels the set buy command
    """
    printCmd(cmdDict)
    CancelSetBuyCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)
    
def CMD_SetBuyTrigger(cmdDict, threadContext, startTime):
    """
        Adds the price trigger to the set buy command
    """
    printCmd(cmdDict)
    SetBuyTriggerCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_SetSellAmt(cmdDict, threadContext, startTime):
    """
        Creates a sell trigger based on the number of stocks the user wants to sell
    """
    
    printCmd(cmdDict)
    SetSellAmtCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_CancelSetSell(cmdDict, threadContext, startTime):
    """
        Cancels the set sell command
    """
    printCmd(cmdDict)
    CancelSetSellCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_SetSellTrigger(cmdDict, threadContext, startTime):
    """
        Adds the price trigger to the set sell command
    """
    printCmd(cmdDict)
    SetSellTriggerCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_Dumplog(cmdDict, threadContext, startTime):
    """
        Print all of the transactions or just the user's transactions
    """
    cmdDict['user'] = 'admin'
    printCmd(cmdDict)
    DumplogCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)


def CMD_DisplaySummary(cmdDict, threadContext, startTime):
    """
        Print the user's account from accounts, transaction history, and buy/sell triggers
    """
    printCmd(cmdDict)
    DisplaySumCmd.execute(cmdDict)
    cmdCompleted(cmdDict, startTime)

def CMD_UserDC(cmdDict, threadContext, startTime):  
    """
        User has disconnected. Clean up thread context and prepare exit. 
    """
    printCmd(cmdDict)
    threadContext["UserConnected"] = False
    cmdCompleted(cmdDict, startTime)

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
    'USER_DISCONNECT'   : CMD_UserDC,
}

