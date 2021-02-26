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
from threading import Thread
from threading import Lock
import datetime as datetime


cmd_print_lock = Lock()
SERV_PORT       = 60000
SERV_HOST_NAME  = '127.0.0.1'

AUDIT_SERV_ADDY = '127.0.0.1'
AUDIT_SERV_PORT = 50000
DEFAULT_WEB_SERV_PORT = 65000

NUM_FORWARD_SERVERS = 1

# Table of open web servers to forward packet requests too. 
#    - user IDs are key- hashed and modulos with NUM of servers
#       this determines the server index to forward user request too
#    - Audit server is always last array index. 
forwardServers = []

PACKET_SIZE     = 8192 

class loadBalancer():

    def __init__(self, port=SERV_PORT, hostname=SERV_HOST_NAME):
        self.port           = port
        self.hostname       = hostname
        self.userProcesses  = {}
        self.serverRunning  = True
        
    def start(self):
        """ starts the webserver up. This includes initializing the socket, 
        binding the socket for recieving, and calling the class listen function"""
        time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        print("-------LOADBALANCER STARTED!-------")
        print("Timestamp: ", time_now)
        print("Port: " + str(self.hostname))
        print("Port: " + str(self.port))
        print()
        
        # Create Listening Socket
        self.socketRevc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socketRevc.bind((self.hostname, self.port))

        except socket.error as err:
            print("ERROR! binding port {self.port} failed with error: {err}")
            self.shutdown()
            sys.exit(1)

        # Create Outgoing sockets for multiple webserver connections
        numberOfServers = len(forwardServers)
        self.serverSockets = [socket.socket(socket.AF_INET, socket.SOCK_STREAM) for _ in range(numberOfServers)]

        for index in range(numberOfServers):
            self.serverSockets[index].connect((forwardServers[index][0], forwardServers[index][1]))


        self.packetQ = queue.Queue()

        # Create the consumer thread to listen for incoming packets. 
        # TODO: Can create consumer thread for each connected webserver. 
        consumerTh = Thread(target=self.consumerThread)
        consumerTh.start()

        # Create the producer thread to listen for incoming packets. 
        producerTh = Thread(target=self.producerThread)
        producerTh.start()

        while True:
            pass

    
    def shutdown(self):
        """ shutsdown the server connection, and socket. """
        try:
            self.serverRunning = False

            self.socketRevc.shutdown(socket.SHUT_RDWR)
            self.socketRevc.close()

            for index in range(forwardServers.size()):
                self.serverSockets[index].shutdown(socket.SHUT_RDWR)
                self.serverSockets[index].close()

            print("~SERVER SHUTDOWN")
            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            print("Timestamp: ", time_now)

            self.packetQ.join()

        except socket.error as err:
            pass

    def producerThread(self):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet.  """

        print("Starting load balancer PRODUCER thread")
        self.socketRevc.listen(5)
        
        while self.serverRunning:
            (conn, address) = self.socketRevc.accept()

            conn.setblocking(False)

            # Start a thread for each socket connection.
            # TODO: Change to be Event driven 
            Thread(target=self.handleConnection, args=(conn, address)).start()

        print("WARNING! Load Balancer producer thread ending")

    def handleConnection(self, conn, address):
        """ Listens to the socket for incoming packets. When a incoming connection
            occurs a thread will be started to recieve and decode the packet. 
            Will add the incoming packets to internal queue for later transmission.
            """

        print("New Client Connection Detected from: {}".format(address))

        while self.serverRunning:
            try:
                data = conn.recv(PACKET_SIZE)
                if not data:
                    # connection has been closed
                    break
            except socket.error as err:
                time.sleep(0.001)
                continue

            strData = str(data).strip("b\"")

            # Sometimes Data packets are bunched up in the read buffer. 
            #   This mechanism will seperate them, and process each
            packets = strData.split("}")

            for userReqData in packets[:-1]:
                userReqData = userReqData.strip() + '}'

                # Decode the packet into a dictionary type
                userDict = ast.literal_eval(str(userReqData))

                # DEBUG PRINT
                #print("Producer -- Putting P on Queue")

                self.packetQ.put(userDict)

        print("Client Closed: {}".format(address))
        conn.close()


    def consumerThread(self):
        """ Consumer thread
    
        """
        print("Starting load balancer CONSUMER thread")

        while self.serverRunning:
            try: 
                packet = self.packetQ.get(False)

                if "user" in packet.keys():
                    user = packet["user"]
                else:
                    user = "default"
                
                serverHash = hash(user) % NUM_FORWARD_SERVERS
                print("Forwarding Packet: [#{}:{}: --> Serv: {})".format(packet["transactionNumber"], user, serverHash))
                
                self.serverSockets[serverHash].send(str(packet).encode())

                self.packetQ.task_done()

            except queue.Empty:
                time.sleep(0.001)
                pass 

        print("WARNING! Load Balancer consumer thread ending")


if __name__ == '__main__':

    print(" ~~~~ WEB SERVER INFORMATION ~~~~")

    while(True):
        webServAddress  = input("\nEnter hostname (localhost default): ") or "localhost"
        webServPort     = int(input("Enter port number ({} default): ".format(DEFAULT_WEB_SERV_PORT)) or DEFAULT_WEB_SERV_PORT)

        forwardServers.append([webServAddress, webServPort])

        print("\nAdding Webserver Connection: {}:{} \n".format(webServAddress, webServPort))

        if "q" == (input("Enter \'q\' to STOP inputing Web Server port/address: ") or "c"):
            break

        DEFAULT_WEB_SERV_PORT += 1
        NUM_FORWARD_SERVERS   += 1

    # TODO: Audit Server 
    #print("\n ~~~~ AUDIT SERVER INFORMATION ~~~~")

    #auditServAddress  = input("\nEnter the Audit Server hostname (localhost default): ") or "localhost"
    #auditServPort     = int(input("Enter port number ({} default): ".format(AUDIT_SERV_PORT)) or AUDIT_SERV_PORT)

    #print("\nAdding Audit Server Connection: {}:{} \n".format(auditServAddress, auditServPort))
    #forwardServers.append([auditServAddress, auditServPort])

    print("SERVER LIST: {} \n\n".format(forwardServers))

    server = loadBalancer()
    server.start()
