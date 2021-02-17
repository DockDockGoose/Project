""" Webserver class definition. This webserver handles the incoming packets from both the
    workload generator and web interface. """

""" TODO: 
        - Change to be a DJango type web server (???) 
        - Make more scalable
        - !!! Add a method to turn off the server (I have no idea, tried signal handler - damon)

    REFERENCES: 
        - https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
        - https://realpython.com/python-sockets/
        """ 

import socket
import sys
import time
import ast
import queue
import user_commands

from user_commands import userCommands
from threading import Lock
from threading import Thread

import datetime as datetime

# Default server values, but can be inputted by user on class initialization
SERV_PORT       = 65000
SERV_HOST_NAME  = '127.0.0.1'

PACKET_SIZE     = 8192

class webServer():

    def __init__(self, port=SERV_PORT, hostname=SERV_HOST_NAME):
        self.port           = port
        self.hostname       = hostname
        self.userProcesses  = {}
        self.serverRunning  = True


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
            print(f"ERROR! binding port {self.port} failed with error: {err}")
            self.socket.close()
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

            self.serverRunning = False

            for threadContext in self.userProcesses:
                # block untill process the last of the thread queue work items  
                threadContext["workQ"].join()

        except socket.error as err:
            pass

    def listen(self):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        self.socket.listen()

        while self.serverRunning:
            (conn, address) = self.socket.accept()
            
            conn.setblocking(False)
            
            # Start a thread for each socket connection.
            # TODO: Change to be Event driven 
            Thread(target=self.handleConnection, args=(conn, address)).start()

        self.shutdown()

    def handleConnection(self, conn, address):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        print("Server Connection Detected from: {}".format(address))

        while self.serverRunning:
            data = []

            try:
                data = conn.recv(PACKET_SIZE)
                if not data:
                    # Connection has been closed
                    break
            except socket.error as err:
                time.sleep(1)
                continue

            print("~~ Read Data ~~")

            # Sometimes Data packets are bunched up in the read buffer. 
            #      This mechanism will seperate them, and process each
            strData = str(data).strip("b\"")
            packets = strData.split("}")

            for userReqData in packets[:-1]:
                self.handleClientRequest(userReqData.strip + '}')


        conn.shutdown(socket.SHUT_RDWR)
        conn.close()
        print("Client Closed: {}".format(address)) 

    def handleClientRequest(self, rawPacket):

        # decode the packet into a dictionary type
        # TODO: sending back data to front end ???
        userReq = ast.literal_eval(str(rawPacket))

        userReq["server"] = SERV_HOST_NAME

        if "user" in userReq.keys():
            # IF user field is specified send to the user process threads.
            user = userReq["user"]

            if user not in self.userProcesses:
                #IF no user process thread created initialize user process thread.
                self.initializeUserThread(user)

            threadContext = self.userProcesses[user]

            # Add user command packet to thread work queue
            threadContext["workQ"].put(userReq)

        else:
            # NO user specified. Dumplog server command. 
            threadContext = self.userProcesses["admin"]

            threadContext["workQ"].put(userReq)


    def initializeUserThread(self, userId):
        """ Every client has an asociated user thread. This thread will handle all of a specific user requests.
            This function will initialize and start the user thread, including its queue, and user ports. """
        
        print("NEW USER! ", userId)

        # Initialize the threadContext associated with the user thread. 
        self.userProcesses[userId] = {
            "userId"        : userId,
            "workQ"         : queue.Queue(),
            "userConnected" : True,
        }

        # Create and Start the user thread
        cReqThread = Thread(target=self.userConsumerThread, args=[userId])
        cReqThread.start()

        return

    def userConsumerThread(self, userId):
        """ This is the user thread associated with each user. Work is recieved from the client
            and put in the associated user work thread queue. The thread will retrieve this work 
            to execute on. """

        print("Starting Thread Process for Client: ", userId)
        threadContext = self.userProcesses[userId]

        processed = 0

        while threadContext["userConnected"]:
            while not threadContext["workQ"].empty():
                # Wait for next work Q item.
                userReq = threadContext["workQ"].get()
                
                print("QUEUE/PROCESSED: {} -- {}".format(threadContext["workQ"].qsize(), processed))

                # Call command function dictionary
                command = userReq["command"]
                userCommands[command](userReq, threadContext, time.time())

                # Indicate that queue work item processed. 
                threadContext["workQ"].task_done()

                processed += 1
            else:
                time.sleep(0.005)

        print("Ending Thread Process for Client: ", userId)


if __name__ == '__main__':
    host_adr    = input("Enter hostname (localhost default): ") or "localhost"
    port        = int(input("Enter port number ({} default): ".format(SERV_PORT)) or SERV_PORT)

    server = webServer(port, host_adr)
    server.start()

