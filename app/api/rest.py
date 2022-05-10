from typing import List

from fastapi import APIRouter, status

from ..models import UserCreate
from ..service.crud import ChatCrud

router = APIRouter()


@router.post('/users', status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate) -> dict[str, int]:
    handler = await ChatCrud.connect_handler()
    user_id = await handler.register_user(user.name)
    return {'id': user_id}


@router.get('/messages', response_model=List[str])
async def get_latest_messages() -> List[str]:
    handler = await ChatCrud.connect_handler()
    return await handler.load_messages()
