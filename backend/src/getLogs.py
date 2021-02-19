import pymongo
import sys
sys.path.append('..')
from audit import logXML as log


DB_NAME = 'mongodb'
DB_PORT = 27017
HOST = 'localhost'


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
    print(processing)
    processing = processing + 1
    if (transact['logType'] == 'userCommand'):
        print(transact)
        log.logEvents['userCommand'](transact)

log.prettyPrintLog()

print("-----COMPLETED LOG-----")
