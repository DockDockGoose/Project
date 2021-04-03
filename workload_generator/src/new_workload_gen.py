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

packetQ = queue.Queue()

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
    user                = requestInfo[1]

    if command == BUY:
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == SELL:
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_BUY_AMOUNT:
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_BUY_TRIGGER :
        try:
            amount = float(requestInfo[3].strip("\n"))
        except ValueError:
            amount = 0.00
        stockSymbol = (requestInfo[2])
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_SELL_AMOUNT:
        (stockSymbol, amount) = (requestInfo[2], float(requestInfo[3].strip("\n")))
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == SET_SELL_TRIGGER:
        try:
            amount = float(requestInfo[3].strip("\n"))
        except ValueError:
            amount = 0.00
        stockSymbol = (requestInfo[2])
        performRequest(transactionNumber, command, user, stockSymbol, amount)

    elif command == QUOTE:
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(transactionNumber, command, user, stockSymbol)

    elif command == CANCEL_SET_BUY:
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(transactionNumber, command, user, stockSymbol)

    elif command == CANCEL_SET_SELL:
        stockSymbol = requestInfo[2].strip("\n")
        performRequest(transactionNumber, command, user, stockSymbol)

    elif command == ADD:
        amount = float(requestInfo[2].strip("\n"))
        performRequest(transactionNumber, command, user, amount=amount)

    elif command == COMMIT_BUY:
        performRequest(transactionNumber, command, user)

    elif command == CANCEL_BUY:
        performRequest(transactionNumber, command, user)

    elif command == COMMIT_SELL:
        performRequest(transactionNumber, command, user)

    elif command == CANCEL_SELL:
        performRequest(transactionNumber, command, user)

    elif command == DISPLAY_SUMMARY:
        performRequest(transactionNumber, command, user)

    elif command == DUMPLOG:
        if len(requestInfo) == 3:
            (user, filename) = (requestInfo[1], requestInfo[2])
            performRequest(transactionNumber, command, user, filename=filename)
            
        elif len(requestInfo) == 2:
            filename = requestInfo[1]
            performRequest(transactionNumber, command, filename=filename)
    
    else:
        logging.warning(f"Invalid request: {requestInfo}")

def performRequest(transactionNumber, command, user=None, stockSymbol=None, amount=None, filename=None):
    request = {'transactionNumber': transactionNumber, 'command': command}
    
    if user:
        request['user'] = user
    if stockSymbol:
        request['stockSymbol'] = stockSymbol
    if amount:
        request['amount'] = amount
    if filename:
        request['fileName'] = filename

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
        except queue.Empty:
            if packetQ.empty():
                    break

        requestStr = str(request).encode()

        s.sendall(requestStr.ljust(256))

        packetQ.task_done()

    time.sleep(2)
    s.shutdown(socket.SHUT_RDWR)
    s.close()
    print("Consumer Thread Finished!")


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

                cThread = Thread(target=consumerThread)
                cThread.start()

                for t in threads:
                    t.join()


                dump_t = Thread(target=send_requests, args=tuple([line]))
                dump_t.start()
                dump_t.join()
                user_commands = {}
                cThread.join()

                print("\n\n\nWorkload Generator Finished!!")

            else:
                user_commands[user] = user_commands.get(user, [])
                user_commands[user].append(line)

    except IOError as err:
        print("I/O error: {}".format(err))
        sys.exit(2)