from typing import Optional

from bson import ObjectId
from pydantic.main import BaseModel


class OID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if v == '':
            raise TypeError('ObjectId is empty')
        if ObjectId.is_valid(v) is False:
            raise TypeError('ObjectId invalid')
        return str(v)


class PostDB(BaseModel):
    id: Optional[OID]
    title: str
    description: str