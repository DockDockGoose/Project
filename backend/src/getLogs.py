import pymongo
import sys
import urllib.parse
sys.path.append('..')
from audit import logXML as log

DB_NAME = 'stocksite_db_dev'
DB_PORT = 27017
HOST = 'localhost'

ERROR_LOG = 'errorEvent'
CMD_LOG = 'userCommand'
QUOTE_LOG = 'quoteServer'
SYSTEM_LOG = 'systemEventType'
TRANSACT_LOG = 'accountTransaction'

TRANSACT_COLLECT = "transactions_transaction"

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

transactions = list(Database[TRANSACT_COLLECT].find())

processing = 0
for transact in transactions:
    try:
        print(processing)
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

    except KeyError as err:
        print(f'Key Error: {err}\n With log: {transact}')

log.prettyPrintLog()

print("-----COMPLETED LOG-----")
