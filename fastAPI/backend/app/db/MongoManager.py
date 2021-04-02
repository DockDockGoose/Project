import logging
from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from db.models import Account, OID

from core.config import database_name, accounts_collection, MONGODB_URL


class MongoManager(object):
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(self, path: str):
        logging.info("Connecting to MongoDB.")
        self.client = AsyncIOMotorClient(path)
        self.db = self.client.stocksite_prod_db
        logging.info("Connected to MongoDB.")

    async def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")

    async def get_database() -> AsyncIOMotorClient:
        return db.client

    async def get_accounts(self) -> List[Account]:
        accounts_list = []
        accounts_q = self.db.accounts.find()
        async for account in accounts_q:
            accounts_list.append(Account(**account, username=account['username']))
        return accounts_list

    async def get_account(self, account_username: OID) -> Account:
        account_q = await self.db.accounts.find_one({'username': ObjectId(account_username)})
        if account_q:
            return Account(**account_q, account_username=account_q['_id'])

    async def delete_account(self, account_username: OID):
        await self.db.accounts.delete_one({'username': ObjectId(account_username)})

    async def update_account(self, account_username: OID, account: Account):
        await self.db.accounts.update_one({'username': ObjectId(account_username)},
                                       {'$set': account.dict(exclude={'_id'})})

    async def add_account(self, account: Account):
        await self.db.accounts.insert_one(account.dict(exclude={'_id'}))