""" Webserver class definition. This webserver handles the incoming packets from both the
    workload generator and web interface. This webserver  """

""" TODO: 
        - Change to be a DJango type web server (???) 
        - Make more scalable
        - !!! Add a method to turn off the server (I have no idea, tried signal handler - damon)
        """ 

import socket
import sys
import time
import ast
import queue
import threading
import user_commands
from user_commands import userCommands
from threading import Lock
import datetime as datetime


SERV_PORT       = 65432
SERV_HOST_NAME  = '127.0.0.1'

PACKET_SIZE     = 1024
thread_print_lk = Lock()

# REFERENCE MATERIALS
# https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
# https://realpython.com/python-sockets/

class webServer():

    def __init__(self, port=SERV_PORT, hostname=SERV_HOST_NAME):
        self.port           = port
        self.hostname       = hostname
        self.userProcesses  = {}
        
    def start(self):
        """ starts the webserver up. This includes initializing the socket, 
        binding the socket for recieving, and calling the class listen function"""
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print("-------SERVER STARTED!-------")
        print("Timestamp: ", time_now)
        print("Port: " + str(self.hostname))
        print("Port: " + str(self.port))
        print()
        
        # Initialize a server administration thread for dumplog command
        self.initializeUserThread("admin")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.hostname, self.port))

        except socket.error as err:
            print("ERROR! binding port {self.port} failed with error: {err}")
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

    def listen(self):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        self.socket.listen(5)

        while True:
            (conn, address) = self.socket.accept()
            conn.settimeout(60)
            self.handleRequest(conn, address)

    def handleRequest(self, conn, address):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """
        # need to enable more threads processing and sending user packets. 
        data = str(conn.recv(PACKET_SIZE))

        # decode the packet into a dictionary type
        # TODO: sending back data to front end ???
        strData = ast.literal_eval(str(data).strip("b\""))
        strData["server"] = SERV_HOST_NAME

        if "user" in strData.keys():
            #IF user field is specified send to the user process threads.
            user = strData["user"]

            if user not in self.userProcesses:
                #IF no user process thread created initialize user process thread.
                self.initializeUserThread(user)

            threadContext = self.userProcesses[user]

            #Add user command packet to thread work queue
            threadContext["workQ"].put(strData)

        else:
            #NO user specified. Assume dumplog server command. 
            threadContext = self.userProcesses["admin"]
            threadContext["workQ"].put(strData)


    def initializeUserThread(self, userId):
        """ Every client has an asociated user thread. This thread will handle all of a specific user requests.
            This function will initialize and start the user thread, including its queue, and user ports. """
        
        print("NEW USER! ", userId)
        # Initialize the threadContext associated with the user thread. 
        self.userProcesses[userId] = {
            "userId" : userId,
            "workQ"  : queue.Queue(),
            "qLock"  : Lock(),
        }

        #Create and Start the user thread
        cReqThread = threading.Thread(target=self.handleClientRequest, args=[userId])
        cReqThread.start()

        return 

    def handleClientRequest(self, userId):
        """ This is the user thread associated with each user. Work is recieved from the client
            and put in the associated user work thread queue. The thread will retrieve this work 
            to execute on. """

        print("Starting Thread Process for Client: ", userId)

        threadContext = self.userProcesses[userId]

        #TODO: allow thread closing here through threadContext. 
        while True:
            #Wait for next work Q item.
            userReq = threadContext["workQ"].get()
            
            #Call command function dictionary
            command = userReq["command"]
            userCommands[command](userReq)


if __name__ == '__main__':
    server = webServer()
    server.start()
