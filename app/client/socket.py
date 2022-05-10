import asyncio

import aiohttp
import typer

from .utils import WORD, get_socket_url


async def send_message(websocket: aiohttp.ClientWebSocketResponse) -> None:
    """Handles user's input and sends it to server"""
    while True:
        message = await asyncio.to_thread(input)
        await websocket.send_str(message)
        if message == WORD.STOP:
            break


async def receive_message(websocket: aiohttp.ClientWebSocketResponse) -> None:
    """Handles received messages and prints in user's console"""
    async for message in websocket:
        if message.type == aiohttp.WSMsgType.TEXT:
            if message.data == WORD.STOP:
                break
            typer.echo(message.data)

        else:
            typer.echo('Something is wrong with server')
            break

    typer.echo('Connection is over!')


async def start_chat(user_id: int) -> None:  # pragma: no cover
    """Handles websocket's loop actions"""
    socket_url = get_socket_url(user_id)
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(socket_url) as ws:
            tasks = [
                asyncio.ensure_future(task(ws))
                for task in (send_message, receive_message)
            ]
            try:
                await asyncio.gather(*tasks)
            except asyncio.exceptions.CancelledError:
                for task in tasks:
                    task.cancel()
