""" Webserver class definition. This webserver handles the incoming packets from both the
    workload generator and web interface. This webserver  """

""" TODO: 
        - Change to be a DJango type web server (???) 
        - Make more scalable
        - Add a method to turn off the server """ 

import socket
import sys
import time
import ast
import threading
import user_commands
from user_commands import userCommands
from threading import Lock
import datetime as datetime


SERV_PORT       = 65432
SERV_HOST_NAME  = '127.0.0.1'

PACKET_SIZE     = 1024
thread_print_lk = Lock()
#REFERENCE MATERIALS
# https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
# https://realpython.com/python-sockets/

class webServer():

    def __init__(self, port=SERV_PORT, hostname=SERV_HOST_NAME):
        self.port       = port
        self.hostname   = hostname

    def start(self):
        """ starts the webserver up. This includes initializing the socket, 
        binding the socket for recieving, and calling the class listen function"""

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((self.hostname, self.port))
            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

            print("-------SERVER STARTED!-------")
            print("Timestamp: ", time_now)
            print("Port: " + str(self.hostname))
            print("Port: " + str(self.port))

        except socket.error as err:
            print("ERROR! binding port {self.port} failed with error: ", err)
            self.shutdown()
            sys.exit(1)

        # Call to the listening function to start recieving and decoding incoming packets
        self.listen()
    
    def shutdown(self):
        """ shutsdown the server connection, and socket. """
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
            print("~SERVER SHUTDOWN")
            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            print("Timestamp: ", time_now)

        except socket.error as err:
            pass

# Change to create thread per user (currently recieves commands out of order)
    def listen(self):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        self.socket.listen(5)

        while True:
            (conn, address) = self.socket.accept()
            conn.settimeout(60)
            threading.Thread(target=self.handleRequest, args=(conn, address)).start()

    def handleRequest(self, conn, address):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        data = str(conn.recv(PACKET_SIZE))
        # decode the packet into a dictionary type
        # TODO: add client port info so we can send back data. 
        strData = ast.literal_eval(str(data).strip("b\""))
        print(strData)
        # Add server to dict
        strData["server"] = SERV_HOST_NAME
        command = strData["command"]
        userCommands[command](strData)


if __name__ == '__main__':
    server = webServer()
    server.start()
    