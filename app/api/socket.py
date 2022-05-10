from fastapi import APIRouter, WebSocket

from ..service.socket import ChatClient

router = APIRouter()


@router.websocket('/ws/{client_id}')
async def connect_websocket(websocket: WebSocket, client_id: int) -> None:
    client_my = await ChatClient.connect_client(str(client_id), websocket)
    await client_my.start_chat()
