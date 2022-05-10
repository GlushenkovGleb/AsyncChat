from typing import List, Optional

import requests
from fastapi import status
from pydantic import BaseModel
from strenum import StrEnum


class Url(StrEnum):
    MESSAGES = 'http://127.0.0.1:8000/messages'
    USER_CREATE = 'http://127.0.0.1:8000/users'
    WEBSOCKET = 'http://127.0.0.1:8000/ws'


class WORD(StrEnum):
    STOP = ':quit'


class User(BaseModel):
    id: int


def load_latest_messages() -> List[str]:
    """Loads the latest messages from server and returns them"""
    response = requests.get(Url.MESSAGES)
    messages = response.json()
    if not messages:
        return ["There's no previous messages"]
    return messages


def register_user(name: str) -> Optional[int]:
    """Registers new user on server and returns user's id"""
    user_dict = {'name': name}
    response = requests.post(Url.USER_CREATE, json=user_dict)

    if response.status_code == status.HTTP_201_CREATED:
        user = User(**response.json())
        return user.id

    return None


def get_socket_url(user_id: int) -> str:
    """Return url for user's websocket connection"""
    return f'{Url.WEBSOCKET}/{user_id}'
