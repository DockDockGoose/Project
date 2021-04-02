# Pydantic Schema's are used for validating data along with 
# serializing (JSON -> Python) and de-serializing (Python -> JSON). 
# It does not serve as a Mongo schema validator

from typing import Optional, List
from bson import ObjectId
from pydantic.main import BaseModel
import pydantic

class OID(ObjectId):
    __origin__ = pydantic.typing.Literal
    __args__ = (str, )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return v

class Stock(BaseModel):
    stockSymbol: str
    price: float
    quoteServerTime: int

class Account(BaseModel):
    username: Optional[OID]
    funds: float
    pendingFunds: float
    stocks: Optional[List[Stock]] = None
    class Config:
        fields = {'username': '_id'}