import socket
import sys

QUOTE_PORT       = 4444
QUOTE_HOST_NAME  = '192.168.4.2'

PACKET_SIZE 	 = 1024


"""
	The real quote server, can be used on the VM
"""

class QuoteServer:
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
			Get a quote from the quote server
		"""

		# Get query and send to quote server
		quote =  cmdDict['stockSymbol'] + ',' + cmdDict['user'] + "\n"
			
		self.socket.send(quote.encode())
		
		# Read and print up to 1k of data.
		try:
			data = self.socket.recv(PACKET_SIZE)
			data = data.decode().split(",")

			quote_data = {
				'price': data[0],
				'stock': data[1],
				'user': data[2],
    			'cryptokey': data[4]
			}

			return quote_data
			
		except:
			print ('Connection to server closed')	
			# close the connection, and the socket
			self.socket.close()

	def dummyGetQuote(self, cmdDict):
		"""
			Use intead of getQuote when you are not connected to server
			Will return dummy data
		"""
		quote_data = {
				'price': 10,
				'stock': cmdDict['stockSymbol'],
				'user': cmdDict['user'],
    			'cryptokey': 'iedfIbDal3nbXUIdp6BwrexrCe6ih3JZlFmjdMUools='
			}
		return quote_data
			
		
if __name__ == '__main__':
	host_adr = input("Enter hostname (192.168.4.2): ") or QUOTE_HOST_NAME
	port = int(input("Enter port number (4444): ") or QUOTE_PORT)
	qs = QuoteServer(host_adr, port)