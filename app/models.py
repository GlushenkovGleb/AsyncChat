from pydantic import BaseModel
from strenum import StrEnum


class UserCreate(BaseModel):
    name: str


class WORD(StrEnum):
    STOP = ':quit'


class StopSocketTasks(Exception):
    pass
