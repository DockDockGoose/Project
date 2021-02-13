import socket
import sys


""" A mock of the quote server. Will return dummy quote."""

class MockQuoteServer:

	QUOTE_PORT       = 65432
	QUOTE_HOST_NAME  = '127.0.0.1'

	def __init__(self, port=QUOTE_PORT, hostname=QUOTE_HOST_NAME):
		self.port 	  = port
		self.hostname = hostname

	def connect(self):
		"""
		Connect to quote server.
		"""

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			print(f"Connecting to {self.host_adr}:{self.port} ...")
			self.socket.connect((self.host_adr, self.port))
		except socket.error as err:
			print(f"ERROR! binding port {self.port} failed with error: {err}")
			self.socket.close()
			sys.exit(1)

	def getQuote(self, cmdDict):
		"""
			Use intead of getQuote when you are not connected to server
			Will return dummy data.
		"""
		
		quote_data = {
				'price': 10,
				'stock': cmdDict['stockSymbol'],
				'user': cmdDict['user'],
    			'cryptokey': 'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools='
		}

		return quote_data