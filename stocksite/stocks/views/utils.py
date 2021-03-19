"""
Utilities file for stocks API.
"""
import socket
import sys
from time import time

""" A mock up of the quote server. Will return dummy quote."""
class MockQuoteServer:
	QUOTE_PORT          =       65432
	QUOTE_HOST_NAME     =       '127.0.0.1'
	mockCryptoKey       =       'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools'

	def __init__(self, port=QUOTE_PORT, hostname=QUOTE_HOST_NAME):
		self.port 	  = port
		self.hostname = hostname

	def getQuote(username, stockSymbol, mockCryptoKey=mockCryptoKey):
		"""
			Use intead of getQuote when you are not connected to server
			Will return dummy data.
		"""
		
		quote_data = {
				'price': 10.50,
				'stockSymbol': stockSymbol,
				'username': username,
				'quoteServerTime': int(time()*1000),
				'cryptoKey': mockCryptoKey
		}

		return quote_data


def getByStockSymbol(stocks, stockSymbol): 
    """
    Searches for the dictionary containing the correct stockSymbol in the list.
    """
    return next((item for item in stocks if item['stockSymbol'] == stockSymbol), None)