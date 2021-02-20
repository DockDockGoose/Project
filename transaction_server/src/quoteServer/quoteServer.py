""" Used to query quotes from the quote server. """

import socket
import sys


QUOTE_PORT       = 4444
QUOTE_HOST_NAME  = '192.168.4.2'

PACKET_SIZE 	 = 1024

class QuoteServer:


	def __init__(self, hostname=QUOTE_HOST_NAME, port=QUOTE_PORT,):
		
		self.hostname = hostname
		self.port     = port

	def connect(self):
		"""
		Connect to quote server.
		"""
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


		try:
			print(f"Connecting to {self.hostname}:{self.port} ...")
			self.socket.connect((self.hostname, self.port))
		except socket.error as err:
			print(f"ERROR! binding port {self.port} failed with error: {err}")
			self.socket.close()
			sys.exit(1)

	def getQuote(self, cmdDict):
		"""
			Get a quote from the quote server
		"""
		# Connect to quote server
		self.connect()

		# Get query and send to quote server
		quote =  cmdDict['stockSymbol'] + ',' + cmdDict['user'] + "\n"
			
		self.socket.send(quote.encode())
		
		# Read and send back 1k of data.
		try:

			data = self.socket.recv(PACKET_SIZE)
			data = data.decode().split(",")

			quote_data = {
				'price': data[0],
				'stock': data[1],
				'user': data[2],
				'timestamp': data[3],
    				'cryptokey': data[4]
			}
			
			# close quote server connection and send back data
			self.socket.close()
			return quote_data	
			
		except:
			print ('Connection to server closed')	
			# close the connection, and the socket
			self.socket.close()

		




