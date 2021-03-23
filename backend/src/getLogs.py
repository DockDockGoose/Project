import pymongo
import sys
import queue
import os
sys.path.append('..')
from audit import logXML as log
from threading import Thread

fileNameQ = queue.Queue()

DB_NAME = 'mongodb'
DB_PORT = 27017
HOST = 'localhost'

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'
SYSTEM_LOG = 'systemEventType'
TRANSACT_LOG = 'accountTransaction'
TRANSACT_COLLECT = "transactions"

auditNum = ""

def consumerThread():
    auditFileName = '../audit/logs/logfile' + auditNum + '.xml'
    logFile = open(auditFileName, "a")
    logFile.writelines(["<?xml version='1.0' encoding='us-ascii'?>", "<log>"])

    while True:
        try:
            # set get to throw exception if no packet in 5 seconds
            filename    = fileNameQ.get(True, 2)
            with open(filename) as tmpLogFile:
                fileContent = tmpLogFile.readlines()

                # Take only the logFile content
                fileContent = fileContent[2:-2]

                # Position logfile at end of file. 
                logFile.seek(0,2)

                logFile.writelines(fileContent)

            os.remove(auditFileName)
            fileNameQ.task_done()
        except queue.Empty:
            if fileNameQ.empty():
                break

    logFile.write("</log>")
    logFile.close()
    print("Consumer Thread Finished!")

#create consumer thread
print("Starting Consumer Thread....")
auditNum = str(input("Enter UserNumber audit number for filename (1 default): ")) or auditNum
cThread = Thread(target=consumerThread)
cThread.start()
print("-----STARTED CONSUMER THREAD-----")

print("Connecting to MongoDB....")
try:
    client = pymongo.MongoClient(HOST, DB_PORT)
    Database = client[DB_NAME]
    print("-----CONNECTED TO MONGODB DB-----")

except pymongo.errors.ConnectionFailure as err:
        print(f"ERROR! Could not connect to database {DB_NAME} failed with error: {err}")
        sys.exit(1)


print("Collecting transactions from the database")
transactions = list(Database[TRANSACT_COLLECT].find())
print("-----COLLECTED TRANSACTIONS-----")


print("Processing transactions...")
processing = 0
for transact in transactions:
    try:
        print("    index: {}".format(processing))
        processing = processing + 1

        # Remove the admin user from dumplog commands
        if (transact['user'] == 'admin'):
            transact.pop('user')

        # Create the correct log based on type
        if (transact['logType'] == CMD_LOG):
            log.logEvents[CMD_LOG](transact)
        elif (transact['logType'] == QUOTE_LOG):
            log.logEvents[QUOTE_LOG](transact)
        elif (transact['logType'] == TRANSACT_LOG):
            log.logEvents[TRANSACT_LOG](transact)
        
        #if (processing % 100000):
        if (processing % 25000):
            log.prettyPrintLog(fileName=processing)
            fileNameQ.put('../audit/logs/tmp/logfile' + str(processing) + '.xml')

    except KeyError as err:
        print(f'Key Error: {err}\n With log: {transact}')

log.prettyPrintLog(fileName=processing)
fileNameQ.put('../audit/logs/tmp/logfile' + str(processing) + '.xml')

print("-----PROCESSED TRANSACTIONS-----")

fileNameQ.join()

print("-----COMPLETED LOG-----")
