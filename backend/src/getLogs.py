import pymongo
import sys
sys.path.append('..')
from audit import logXML as log


DB_NAME = 'mongodb'
DB_PORT = 27017
HOST = 'localhost'

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'
SYSTEM_LOG = 'systemEventType'
TRANSACT_LOG = 'accountTransaction'

TRANSACT_COLLECT = "transactions"

try:
    client = pymongo.MongoClient(HOST, DB_PORT)
    Database = client[DB_NAME]
    print("-----CONNECTED TO MONGODB DB-----")

except pymongo.errors.ConnectionFailure as err:
        print(f"ERROR! Could not connect to database {DB_NAME} failed with error: {err}")
        sys.exit(1)

transactions = list(Database[TRANSACT_COLLECT].find())

processing = 0
for transact in transactions:
    try:
        print(processing)
        processing = processing + 1
        if (transact['logType'] == CMD_LOG):
            log.logEvents[CMD_LOG](transact)
        elif (transact['logType'] == QUOTE_LOG):
            log.logEvents[QUOTE_LOG](transact)
        elif (transact['logType'] == TRANSACT_LOG):
            log.logEvents[TRANSACT_LOG](transact)

    except KeyError as err:
        print(f'Key Error: {err}\n With log: {transact}')

log.prettyPrintLog()

print("-----COMPLETED LOG-----")
