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
import requests
from threading import Thread

defaultTestFile = "../workloads/WL_1_USER.txt"

serverAddress   = "localhost"
serverPort      = "80"

serverURL       = "http://" + serverAddress  + ":" + serverPort + "/"

API_STOCKS_PATH     = "api/stocks/"
API_ACCOUNTS_PATH   = "api/accounts/"
API_TRIGGERS_PATH   = "api/triggers/"

ADD                 = "ADD"
QUOTE               = "QUOTE"
BUY                 = "BUY"
COMMIT_BUY          = "COMMIT_BUY"
CANCEL_BUY          = "CANCEL_BUY"
SELL                = "SELL"
COMMIT_SELL         = "COMMIT_SELL"
CANCEL_SELL         = "CANCEL_SELL"
SET_BUY_AMOUNT      = "SET_BUY_AMOUNT"
CANCEL_SET_BUY      = "CANCEL_SET_BUY"
SET_BUY_TRIGGER     = "SET_BUY_TRIGGER"
SET_SELL_AMOUNT     = "SET_SELL_AMOUNT"
SET_SELL_TRIGGER    = "SET_SELL_TRIGGER"
CANCEL_SET_SELL     = "CANCEL_SET_SELL"
DUMPLOG             = "DUMPLOG"
DISPLAY_SUMMARY     = "DISPLAY_SUMMARY"

GET                 = "GET"
POST                = "POST"
PUT                 = "PUT"
DELETE              = "DELETE"

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
                user = userQ.get()
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
            transactionNumber   = tokens[0].translate(translation)
            requestInfo         = tokens[1].split(",")
            command             = requestInfo[0]
            url             = serverURL

            if command == BUY:
                url += API_STOCKS_PATH + "buy/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

            elif command == SELL:
                url += API_STOCKS_PATH + "sell/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_AMOUNT:
                url += API_TRIGGERS_PATH +  "setbuyamount/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(url, POST, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_TRIGGER :
                url += API_TRIGGERS_PATH +  "setbuytrigger/"
                try:
                    amount = float(requestInfo[3].strip("\n"))
                except ValueError:
                    amount = 0.00
                stockSymbol = (requestInfo[2])
                self.performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_AMOUNT:
                url += API_TRIGGERS_PATH + "setsellamount/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(url, POST, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_TRIGGER:
                url += API_TRIGGERS_PATH + "setselltrigger/"
                try:
                    amount = float(requestInfo[3].strip("\n"))
                except ValueError:
                    amount = 0.00
                stockSymbol = (requestInfo[2])
                self.performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

            elif command == QUOTE:
                url += API_STOCKS_PATH + "quote/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(url, GET, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_BUY:
                url += API_TRIGGERS_PATH + "cancelsetbuy/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(url, DELETE, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_SELL:
                url += API_TRIGGERS_PATH + "cancelsetsell/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(url, DELETE, transactionNumber, command, user, stockSymbol)

            elif command == ADD:
                url += API_ACCOUNTS_PATH + "add/"
                amount = float(requestInfo[2].strip("\n"))
                self.performRequest(url, POST, transactionNumber, command, user, amount=amount)

            elif command == COMMIT_BUY:
                url += API_STOCKS_PATH + "commitbuy/"
                self.performRequest(url, POST, transactionNumber, command, user)

            elif command == CANCEL_BUY:
                url += API_STOCKS_PATH + "cancelbuy/"
                self.performRequest(url, DELETE, transactionNumber, command, user)

            elif command == COMMIT_SELL:
                url += API_STOCKS_PATH + "commitsell/"
                self.performRequest(url, POST, transactionNumber, command, user)

            elif command == CANCEL_SELL:
                url += API_STOCKS_PATH + "cancelsell/"
                self.performRequest(url, DELETE, transactionNumber, command, user)

            elif command == DISPLAY_SUMMARY:
                url += API_ACCOUNTS_PATH + "displaysummary/"
                self.performRequest(url, GET, transactionNumber, command, user)

            elif command == DUMPLOG:
                url += API_ACCOUNTS_PATH + "dumplog/"
                if len(requestInfo) == 3:
                    (user, filename) = (requestInfo[1], requestInfo[2])
                    self.performRequest(url, GET, transactionNumber, command, user, filename=filename)
                    
                elif len(requestInfo) == 2:
                    filename = requestInfo[1]
                    self.performRequest(url, GET, transactionNumber, command, filename=filename)
            
            else:
                logging.warning(f"Invalid request: {requestInfo}")

        f.close()


    def performRequest(self, url, method, transactionNumber, command, user=None, stockSymbol=None, amount=None, filename=None):
        request = {'postUrl': url, 'method': method, 'transactionNum': transactionNumber, 'command': command}

        if user:
            request['username'] = user
        if stockSymbol:
            request['stockSymbol'] = stockSymbol
        if amount:
            request['amount'] = amount
        if filename:
            request['fileName'] = filename

        packetQ.put(request)


def spawnHandlers(userList, handler):
    for i, user in enumerate(userList):
        t = Thread(target=handler, args=(i,))
        t.daemon = True
        t.start()

    cThread = Thread(target=consumerThread)
    cThread.start()
    print("Started {} user handlers".format(i))

def consumerThread():
    while True:
        try:
            # set get to throw exception if no packet in 5 seconds
            request = packetQ.get(True, 2)
        except queue.Empty:
            if userQ.empty():
                    break

        
        if request['method'] == GET:
            r = requests.get(request['postUrl'], json=request)
        elif request['method'] == POST:
            r = requests.post(request['postUrl'], json=request)
        elif request['method'] == PUT:
            r = requests.put(request['postUrl'], json=request)
        elif request['method'] == DELETE:
            r = requests.delete(request['postUrl'], json=request)

        print("HTTP Status:  {}".format(r.status_code))
        print("Command Number:  {}".format(request['transactionNum']))

        packetQ.task_done()

    r.close()
    print("Consumer Thread Finished!")


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