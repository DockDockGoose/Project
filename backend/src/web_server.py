
import socket
import signal
import sys
import time
import threading
import datetime as datetime

SERV_PORT       = 65432
SERV_HOST_NAME  = '127.0.0.1'


#REFERENCE MATERIALS
# https://gist.github.com/joncardasis/cc67cfb160fa61a0457d6951eff2aeae
# https://realpython.com/python-sockets/

class webServer():

    def __init__(self, port=SERV_PORT, hostname=SERV_HOST_NAME):
        self.port       = port
        self.hostname   = hostname

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((self.hostname, self.port))
            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())

            print("-------SERVER STARTED!-------")
            print("Timestamp: ", time_now)
            print("Port: " + str(self.hostname))
            print("Port: " + str(self.port))

        except socket.error as err:
            print("ERROR! binding port {self.port} failed with error: {err}")
            self.shutdown()
            sys.exit(1)

        self.listen()
    
    def shutdown(self):
        try:
            print("~SERVER SHUTDOWN")
            time_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            print("Timestamp: ", time_now)

        except socket.error as err:
            pass

    def listen(self):
        self.socket.listen(5)
       
        while True:
            (conn, addy) = self.socket.accept()
            conn.settimeout(60)
            print("Recieved Connection from: " + str(addy))
            data = conn.recv(1024)
            if not data:
                break;
            else:
                print(data)


def shutdownServer(sig, unused):
    server.shutdown()
    sys.exit(1)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdownServer)

    server = webServer()

    server.start()
    print("Press Ctrl+C to shut down server.")
