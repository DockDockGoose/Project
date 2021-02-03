# Workload Generator (v1) #

""" Contains dictionary of the commands for each user command that can be specified. 
    each user command is set to this function after decoding the packet in the webserver
    """
""" TODO: 
        - finish all commandws
        - inferface with the SQL database. 
        - each command needs to log to the specified xml document
""" 
from threading import Lock
cmd_print_lock = Lock()

def printCmd(cmdDict):
    with cmd_print_lock:
        command = cmdDict["command"]
        print("PACKET CONTENTS:", cmdDict)
        print("    Trans. #: ",   cmdDict["transactionNumber"])
        print("    CMD:      ",   command)

def CMD_Add(cmdDict):
    printCmd(cmdDict)

def CMD_Quote(cmdDict):
    printCmd(cmdDict)

def CMD_Buy(cmdDict):
    printCmd(cmdDict)

def CMD_CommitBuy(cmdDict):
    printCmd(cmdDict)

def CMD_CancelBuy(cmdDict):
    printCmd(cmdDict)

def CMD_Sell(cmdDict):
    printCmd(cmdDict)

def CMD_CommitSell(cmdDict):
    printCmd(cmdDict)

def CMD_CancelSell(cmdDict):
    printCmd(cmdDict)

def CMD_SetBuyAmt(cmdDict):
    printCmd(cmdDict)

def CMD_CancelSetBuy(cmdDict):
    printCmd(cmdDict)

def CMD_SetBuyTrigger(cmdDict):
    printCmd(cmdDict)

def CMD_SetSellAmt(cmdDict):
    printCmd(cmdDict)

def CMD_CancelSetSell(cmdDict):
    printCmd(cmdDict)

def CMD_SetSellTrigger(cmdDict):
    printCmd(cmdDict)

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
