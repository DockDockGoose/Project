'''
    Contains mock data and the method call for each user command
    Used for testing usercommands 
'''

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

set_buy_amount_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'SET BUY AMOUNT',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
    'amount': 100
}

#CMD_SetBuyAmt(set_buy_amount_data)


cancel_set_buy_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'CANCEL SET BUY TRIGGER',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
}

#CMD_CancelSetBuy(cancel_set_buy_data)

set_buy_trigger_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'SET BUY TRIGGER',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
    'amount': 100
}

#CMD_SetBuyTrigger(set_buy_trigger_data)

set_sell_amount_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'SET SELL AMOUNT',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
    'amount': 5
}

#CMD_SetSellAmt(set_sell_amount_data)

set_sell_trigger_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'SET SELL AMOUNT',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
    'amount': 10
}

#CMD_SetSellTrigger(set_sell_trigger_data)

cancel_set_sell_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'CANCEL SET SELL TRIGGER',
    'user': 'oY01WVirLr',
    'stockSymbol': 'S',
}

#CMD_CancelSetSell(cancel_set_sell_data)

dumplog_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'DUMPLOG',
    'filename': 'dumplog1.txt',
    'user': 'oY01WVirLr'
}

#CMD_Dumplog(dumplog_data)


display_data = {
    'pid': 124,
    'transactionNumber': 1,
    'command': 'DISPLAY SUMMARY',
    'user': 'oY01WVirLr'
}

#CMD_DisplaySummary(display_data)
