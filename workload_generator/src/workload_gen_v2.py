
""" Takes workload file and partitions commands per user (retains transaction number & related info).  
    Writes each users commands in [user].txt. Spawns threads per user (dynamically adjusts port). 
    Reads [user].txt to parse and send requested commands in JSON format to specified server.   """

""" TODO: 
        - Modify/Improve command requesting (sends DUMPLOG not last)     """ 


import sys
import re
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

def send_requests(*uCmdList):
    for cmd in uCmdList:
        sendWorkload(cmd)
        time.sleep(0.5)

def sendWorkload(line):
    translation = {91: None, 93: None}

    tokens = line.split(" ")
    transactionNumber   = tokens[0].translate(translation)
    requestInfo         = tokens[1].split(",")
    command             = requestInfo[0]
    url                 = serverURL

    if command == BUY:
        url += API_STOCKS_PATH + "buy/"
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

    elif command == SELL:
        url += API_STOCKS_PATH + "sell/"
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_BUY_AMOUNT:
        url += API_TRIGGERS_PATH +  "setbuyamount/"
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(url, POST, transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_BUY_TRIGGER :
        url += API_TRIGGERS_PATH +  "setbuytrigger/"
        try:
            amount = float(requestInfo[3].strip("\n"))
        except ValueError:
            amount = 0.00
        stockSymbol = (requestInfo[2])
        performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_SELL_AMOUNT:
        url += API_TRIGGERS_PATH + "setsellamount/"
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(url, POST, transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_SELL_TRIGGER:
        url += API_TRIGGERS_PATH + "setselltrigger/"
        try:
            amount = float(requestInfo[3].strip("\n"))
        except ValueError:
            amount = 0.00
        stockSymbol = (requestInfo[2])
        performRequest(url, PUT, transactionNumber, command, user, stockSymbol, amount)

    elif command == QUOTE:
        url += API_STOCKS_PATH + "quote/"
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(url, GET, transactionNumber, command, user, stockSymbol)

    elif command == CANCEL_SET_BUY:
        url += API_TRIGGERS_PATH + "cancelsetbuy/"
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(url, DELETE, transactionNumber, command, user, stockSymbol)

    elif command == CANCEL_SET_SELL:
        url += API_TRIGGERS_PATH + "cancelsetsell/"
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(url, DELETE, transactionNumber, command, user, stockSymbol)

    elif command == ADD:
        url += API_ACCOUNTS_PATH + "add/"
        amount = float(requestInfo[2].strip("\n"))
        performRequest(url, POST, transactionNumber, command, user, amount=amount)

    elif command == COMMIT_BUY:
        url += API_STOCKS_PATH + "commitbuy/"
        performRequest(url, POST, transactionNumber, command, user)

    elif command == CANCEL_BUY:
        url += API_STOCKS_PATH + "cancelbuy/"
        performRequest(url, DELETE, transactionNumber, command, user)

    elif command == COMMIT_SELL:
        url += API_STOCKS_PATH + "commitsell/"
        performRequest(url, POST, transactionNumber, command, user)

    elif command == CANCEL_SELL:
        url += API_STOCKS_PATH + "cancelsell/"
        performRequest(url, DELETE, transactionNumber, command, user)

    elif command == DISPLAY_SUMMARY:
        url += API_ACCOUNTS_PATH + "displaysummary/"
        performRequest(url, GET, transactionNumber, command, user)

    elif command == DUMPLOG:
        url += API_ACCOUNTS_PATH + "dumplog/"
        if len(requestInfo) == 3:
            (user, filename) = (requestInfo[1], requestInfo[2])
            performRequest(url, GET, transactionNumber, command, user, filename=filename)
            
        elif len(requestInfo) == 2:
            filename = requestInfo[1]
            performRequest(url, GET, transactionNumber, command, filename=filename)
    
    else:
        logging.warning(f"Invalid request: {requestInfo}")

def performRequest(url, method, transactionNumber, command, user=None, stockSymbol=None, amount=None, filename=None):
    request = {'postUrl': url, 'method': method, 'transactionNum': transactionNumber, 'command': command}
    if user:
        request['username'] = user
    if stockSymbol:
        request['stockSymbol'] = stockSymbol
    if amount:
        request['amount'] = amount
    if filename:
        request['fileName'] = filename

    if method == GET:
        r = requests.get(request['postUrl'], json=request)
    elif method == POST:
        r = requests.post(request['postUrl'], json=request)
    elif method == PUT:
        r = requests.put(request['postUrl'], json=request)
    elif method == DELETE:
        r = requests.delete(request['postUrl'], json=request)

    if (r.status_code != 200):
        print("Command Number:  {}".format(request['transactionNum']))
        print("HTTP Status:     {}".format(r.status_code))

    r.close()

tasks = []
threads = []
user_commands = {}
translation = {91: None, 93: None}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        defaultTestFile = "../workloads/WL_1_USER.txt"
        testFile = defaultTestFile
        logging.warning(f"Workload Generator will use default file: {testFile[13:]}")
    else:
        testFile = sys.argv[1]
        logging.warning(f"Workload Generator will use: {testFile}")

    try:
        lines = [line.rstrip('\n') for line in open(testFile)]
        count = len(lines)

        print("\nCreating Workload Generator UserCmdLists...")

        for i in range(count):
            line = lines[i]
            tokens = line.split(" ")
            requestInfo         = tokens[1].split(",")
            command             = requestInfo[0]
            user                = requestInfo[1]

            if command == DUMPLOG or i == count-1:
                print("... Success!")
                print("\nSpawning User Handlers...")
                for user in user_commands:
                    t = Thread(target=send_requests, args=tuple(user_commands[user]))
                    t.start()
                    threads.append(t)

                for t in threads:
                    t.join()

                dump_t = Thread(target=send_requests, args=tuple([line]))
                dump_t.start()
                dump_t.join()
                user_commands = {}

                print("\n\n\nWorkload Generator Finished!!")

            else:
                user_commands[user] = user_commands.get(user, [])
                user_commands[user].append(line)

    except IOError as err:
        print("I/O error: {}".format(err))
        sys.exit(2)