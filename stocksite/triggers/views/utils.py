"""
Utilities file for Triggers API.
"""

def getByStockSymbol(stocks, stockSymbol): 
    """
    Searches for the dictionary containing the correct stockSymbol in the list.
    """
    return next((item for item in stocks if item['stockSymbol'] == stockSymbol), None)