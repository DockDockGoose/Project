from fastapi import APIRouter, Depends

from db import MongoManager, connect_to_database
from db.models import Account, PostDB, OID

router = APIRouter()


@router.get('/accounts')
async def get_all_accounts(db: MongoManager = Depends(connect_to_database)):
    accounts = await db.get_accounts()
    return accounts


@router.get('/{account_username}')
async def get_account(account_username: str, db: MongoManager = Depends(connect_to_database)):
    account = await db.get_account(account_username=account_username)
    return account


@router.put('/{account_username}')
async def update_account(account_username: str, account: Account, db: MongoManager = Depends(connect_to_database)):
    account = await db.update_post(account=account, account_username=account_username)
    return account


@router.post('/add/{account_username}', status_code=201)
async def add_account(account_response: Account, db: MongoManager = Depends(connect_to_database)):
    account = await db.add_account(account_response)
    return account


@router.delete('/{account_username}')
async def delete_post(account_username: str, db: MongoManager = Depends(connect_to_database)):
    await db.delete_post(account_username=account_username)