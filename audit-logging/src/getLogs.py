import pymongo
import sys
import urllib.parse
import queue
import os
sys.path.append('..')
from audit import logXML as log
from threading import Thread

fileNameQ = queue.Queue()

DB_NAME = 'stocksite_db_prod'
DB_PORT = 27017
HOST = 'localhost:27018'        # Ran production setup and WL Gen in Windows 10 and Docker got confused.. had to expose a different port than mongo uses internally.

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'
SYSTEM_LOG = 'systemEventType'
TRANSACT_LOG = 'accountTransaction'

TRANSACT_COLLECT = "transactions_transaction"

auditNum = ""

def consumerThread():
    auditFileName = '../audit/logs/logfile' + auditNum + '.xml'
    logFile = open(auditFileName, "a")
    logFile.writelines(["<?xml version='1.0' encoding='us-ascii'?>\n", "<log>\n"])

    while True:
        try:
            # set get to throw exception if no packet in 5 seconds
            filename    = fileNameQ.get(True, 30)

            print("Writing to file: {}".format(filename))

            with open(filename) as tmpLogFile:
                fileContent = tmpLogFile.readlines()

                # Take only the logFile content
                fileContent = fileContent[2:-1]

                # Position logfile at end of file. 
                logFile.seek(0,2)

                logFile.writelines(fileContent)

            os.remove(filename)

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
    #password = input("Please enter database password: ")
    client = pymongo.MongoClient(HOST, username='root', password='dockdockgoose')
    Database = client[DB_NAME]
    print("-----CONNECTED TO MONGODB DB-----")

except pymongo.errors.ConnectionFailure as err:
    print(f"ERROR! Could not connect to database {DB_NAME} failed with error: {err}")
    sys.exit(1)

for coll in Database.list_collection_names():
    print(coll)


print("Collecting transactions from the database")
transactions = list(Database[TRANSACT_COLLECT].find())
print("-----COLLECTED TRANSACTIONS-----")


print("Processing transactions...")
processing = 0
for transact in transactions:
    try:
        print(processing)
        # print(transact)
        #print("    index: {}".format(processing))
        processing = processing + 1

        # Remove the admin user from dumplog commands
        if (transact['username'] == 'admin'):
            transact.pop('username')

        # Create the correct log based on type
        if (transact['type'] == CMD_LOG):
            log.logEvents[CMD_LOG](transact)
        elif (transact['type'] == QUOTE_LOG):
            log.logEvents[QUOTE_LOG](transact)
        elif (transact['type'] == TRANSACT_LOG):
            log.logEvents[TRANSACT_LOG](transact)
        
        if not (processing % 50000):
            log.prettyPrintLog(fileName=processing)
            fileNameQ.put('../audit/logs/tmp/logfile' + str(processing) + '.xml')

    except KeyError as err:
        print(f'Key Error: {err}\n With log: {transact}')

log.prettyPrintLog(fileName=processing)
fileNameQ.put('../audit/logs/tmp/logfile' + str(processing) + '.xml')

print("-----PROCESSED TRANSACTIONS-----")

fileNameQ.join()

print("-----COMPLETED LOG-----")
