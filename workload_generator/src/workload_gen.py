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
#import requests
from threading import Thread

defaultTestFile = "../workloads/WL_1_USER.txt"

serverAddress   = "localhost"
serverPort      = "8000"

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

userQ = queue.Queue()

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
            except:
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
            postUrl             = serverURL

            if command == BUY:
                postUrl += API_STOCKS_PATH + "buy/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == SELL:
                postUrl += API_STOCKS_PATH + "sell/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_AMOUNT:
                postUrl += API_TRIGGERS_PATH +  "setbuyamount/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_BUY_TRIGGER :
                postUrl += API_TRIGGERS_PATH +  "setbuytrigger/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_AMOUNT:
                postUrl += API_TRIGGERS_PATH + "setsellamount/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == SET_SELL_TRIGGER:
                postUrl += API_TRIGGERS_PATH + "setselltrigger/"
                (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol, amount)

            elif command == QUOTE:
                postUrl += API_STOCKS_PATH + "quote/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_BUY:
                postUrl += API_TRIGGERS_PATH + "cancelsetbuy/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol)

            elif command == CANCEL_SET_SELL:
                postUrl += API_TRIGGERS_PATH + "cancelsetsell/"
                stockSymbol = requestInfo[2].strip("\n")
                self.performRequest(postUrl, transactionNumber, command, user, stockSymbol)

            elif command == ADD:
                postUrl += API_STOCKS_PATH + "add/"
                amount = float(requestInfo[2].strip("\n"))
                self.performRequest(postUrl, transactionNumber, command, user, amount=amount)

            elif command == COMMIT_BUY:
                postUrl += API_STOCKS_PATH + "commitbuy/"
                self.performRequest(postUrl, transactionNumber, command, user)

            elif command == CANCEL_BUY:
                postUrl += API_STOCKS_PATH + "cancelbuy/"
                self.performRequest(postUrl, transactionNumber, command, user)

            elif command == COMMIT_SELL:
                postUrl += API_STOCKS_PATH + "commitsell/"
                self.performRequest(postUrl, transactionNumber, command, user)

            elif command == CANCEL_SELL:
                postUrl += API_STOCKS_PATH + "cancelsell/"
                self.performRequest(postUrl, transactionNumber, command, user)

            elif command == DISPLAY_SUMMARY:
                postUrl += API_ACCOUNTS_PATH + "displaysummary/"
                self.performRequest(postUrl, transactionNumber, command, user)

            elif command == DUMPLOG:
                postUrl += API_ACCOUNTS_PATH + "dumplog/"
                if len(requestInfo) == 3:
                    (user, filename) = (requestInfo[1], requestInfo[2])
                    self.performRequest(postUrl, transactionNumber, command, user, filename=filename)
                    
                elif len(requestInfo) == 2:
                    filename = requestInfo[1]
                    self.performRequest(postUrl, transactionNumber, command, filename=filename)
            
            else:
                logging.warning(f"Invalid request: {requestInfo}")

        f.close()

    def performRequest(self, postUrl, transactionNumber, command, user=None, stockSymbol=None, amount=None, filename=None):
        request = {'transactionNumber': transactionNumber, 'command': command}

        if user:
            request['user'] = user
        if stockSymbol:
            request['stockSymbol'] = stockSymbol
        if amount:
            request['amount'] = amount
        if filename:
            request['filename'] = filename
        print(postUrl)

        #r = requests.post(postUrl, json=command_dict)
        # TODO: might need r.close() if get error with too many files open or open sockets. 
        #print("HTTP Status:  {}".format(r.status_code))


def spawnHandlers(userList, handler):

    for i, user in enumerate(userList):
        t = Thread(target=handler, args=(i,))
        t.daemon = True
        t.start()
        

if __name__ == '__main__':
    if len(sys.argv) < 2:
        testFile = defaultTestFile
        logging.warning(f"Workload Generator will use default file: {testFile[13:]}")
    else:
        testFile = sys.argv[1]
        logging.warning(f"Workload Generator will use: {testFile}")

    wg = WorkloadGenerator(testFile)
    spawnHandlers(wg.userList, wg.workloadHandler)

    for user in wg.userList:
        userQ.put(user)

    userQ.join()
