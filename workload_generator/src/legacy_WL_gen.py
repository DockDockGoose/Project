# Workload Generator (v1) #
""" Takes workload file and partitions commands per user (retains transaction number & related info).  
    Writes each users commands in [user].txt. Spawns threads per user (dynamically adjusts port). 
    Reads [user].txt to parse and send requested commands in JSON format to specified server.   """
""" TODO: 
        - Modify/Improve command requesting (sends DUMPLOG not last)     """ 
import sys
import re
import socket
import logging
import queue
import time
from threading import Thread

defaultTestFile = "../workloads/WL_1_USER.txt"
serverAddress   = "localhost"
serverPort      = 60000

ADD = "ADD"
QUOTE = "QUOTE"
BUY = "BUY"
COMMIT_BUY = "COMMIT_BUY"
CANCEL_BUY = "CANCEL_BUY"
SELL = "SELL"
COMMIT_SELL = "COMMIT_SELL"
CANCEL_SELL = "CANCEL_SELL"
SET_BUY_AMOUNT = "SET_BUY_AMOUNT"
CANCEL_SET_BUY = "CANCEL_SET_BUY"
SET_BUY_TRIGGER = "SET_BUY_TRIGGER"
SET_SELL_AMOUNT = "SET_SELL_AMOUNT"
SET_SELL_TRIGGER = "SET_SELL_TRIGGER"
CANCEL_SET_SELL = "CANCEL_SET_SELL"
DUMPLOG = "DUMPLOG"
DISPLAY_SUMMARY = "DISPLAY_SUMMARY"

userQ = queue.Queue()
packetQ = queue.Queue()

class WorkloadGenerator:
    def __init__(self, testFile):
        self.testFile = testFile
        self.userList = self.processFile()

    def processFile(self):
        cmdDict = {}
        userList = []
        try:
            f = open(self.testFile, 'r')
            rawList = re.split("\n", f.read())
            f.close()
        except IOError:
            logging.error(f"Error reading file '{testFile}'.")
            sys.exit()
        for i, commandLine in enumerate(rawList):
            tokens = commandLine.split(" ")
            cmdInfo = tokens[1].split(",")
            user = cmdInfo[1]
            if cmdInfo[0] == DUMPLOG:
                if DUMPLOG in cmdDict:
                    cmdDict[DUMPLOG] += commandLine
                else:
                    userList.append(DUMPLOG)
                    cmdDict[DUMPLOG] = commandLine
            else:
                if user not in userList:
                    userList.append(user)
                if user in cmdDict:
                    cmdDict[user] += commandLine + "\n"
                else:
                    cmdDict[user] = commandLine + "\n"
        for user in userList:
            try:
                f = open((user + ".txt"), "w")
                f.write(cmdDict[user])
                f.close()
            except IOError:
                logging.error(f"Error opening file for writing '{user}'.txt")
        
        if DUMPLOG in cmdDict:
            try:
                f = open((DUMPLOG + ".txt"), "w")
                f.write(cmdDict[DUMPLOG])
                f.close()
            except IOError:
                logging.error(f"Error opening file for writing '{DUMPLOG}'.txt")
        
        return userList


    def workloadHandler(self, pid):
        while True:
            try: 
                user = userQ.get(True, timeout=0.5)
                self.sendWorkload(user, pid)
                userQ.task_done()
            except queue.Empty:
                if userQ.empty():
                    break



    def sendWorkload(self, user, pid):
        translation = {91: None, 93: None}
        
        try:
            f = open(user + ".txt", "r")
        except IOError:
            logging.error(f"Error reading file: '{user}'.txt")

        for line in f:
            tokens = line.split(" ")
            transactionNumber = tokens[0].translate(translation)
            requestInfo = tokens[1].split(",")
            command = requestInfo[0]

            if command == BUY:
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == SELL:
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_AMOUNT:
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_TRIGGER :
                try:
                    amount = float(requestInfo[3].strip("\n"))
                except ValueError:
                    amount = 0.00
                stockSymbol = (requestInfo[2])
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_AMOUNT:
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_TRIGGER:
                try:
                    amount = float(requestInfo[3].strip("\n"))
                except ValueError:
                    amount = 0.00
                stockSymbol = (requestInfo[2])
                self.performRequest(pid, transactionNumber, command, user, stockSymbol, amount)

            elif command == QUOTE:
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(pid, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_BUY:
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(pid, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_SELL:
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(pid, transactionNumber, command, user, stockSymbol)

            elif command == ADD:
                amount = float(requestInfo[2].strip("\n"))
                self.performRequest(pid, transactionNumber, command, user, amount=amount)

            elif command == COMMIT_BUY:
                self.performRequest(pid, transactionNumber, command, user)

            elif command == CANCEL_BUY:
                self.performRequest(pid, transactionNumber, command, user)

            elif command == COMMIT_SELL:
                self.performRequest(pid, transactionNumber, command, user)

            elif command == CANCEL_SELL:
                self.performRequest(pid, transactionNumber, command, user)

            elif command == DISPLAY_SUMMARY:
                self.performRequest(pid, transactionNumber, command, user)

            elif command == DUMPLOG:
                if len(requestInfo) == 3:
                    (user, filename) = (requestInfo[1], requestInfo[2])
                    self.performRequest(pid, transactionNumber, command, user, filename=filename)

                elif len(requestInfo) == 2:
                    filename = requestInfo[1]
                    self.performRequest(pid, transactionNumber, command, filename=filename)

            else:
                logging.warning(f"Invalid request: {requestInfo}")

        f.close()

        
    def performRequest(self, pid, transactionNumber, command, user=None, stockSymbol=None, amount=None, filename=None):
        request = {'transactionNumber': transactionNumber, 'command': command}

        if user:
            request['user'] = user
        if stockSymbol:
            request['stockSymbol'] = stockSymbol
        if amount:
            request['amount'] = amount
        if filename:
            request['filename'] = filename

        try:
            packetQ.put(request)
        except socket.error as err:
            logging.error(f"Queue Put failured with: {err}")
            sys.exit()

def consumerThread():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((serverAddress, serverPort))

    while True:
        try:
            # set get to throw exception if no packet in 5 seconds
            request = packetQ.get(True, 2)
        except:
            break

        requestStr = str(request).encode()

        s.sendall(requestStr.ljust(256))

        packetQ.task_done()

    time.sleep(2)
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    print("Consumer Thread Finished!")


def spawnHandlers(userList, handler):

    for i, user in enumerate(userList):
        t = Thread(target=handler, args=(i,))
        t.daemon = True
        t.start()
    print("Started {} user handlers".format(i))

    cThread = Thread(target=consumerThread)
    cThread.start()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        testFile = defaultTestFile
        logging.warning(f"Workload Generator will use default file: {testFile[13:]}")
    else:
        testFile = sys.argv[1]
        logging.warning(f"Workload Generator will use: {testFile}")

    print("\nCreating Workload Generator User Command Files...")
    wg = WorkloadGenerator(testFile)
    print("... Success!")

    print("\nUser Count: {}".format( len(wg.userList)))
    for user in wg.userList:
        userQ.put(user)

    print("\nSpawning User Handlers...")
    spawnHandlers(wg.userList, wg.workloadHandler)
    print("\nWaiting for all tasks to finish...")

    userQ.join()
    packetQ.join()
    print("\n\n\nWorkload Generator Finished!!")