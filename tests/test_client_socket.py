import pytest
from aiohttp import web

from app.client.socket import receive_message, send_message
from app.client.utils import WORD


@pytest.fixture()
def mock_to_thread_input(mocker):
    return mocker.patch('app.client.socket.asyncio.to_thread')


async def test_websocket_receive(loop, aiohttp_client) -> None:
    async def handler(request):
        ws = web.WebSocketResponse()
        if not ws.can_prepare(request):
            return web.HTTPUpgradeRequired()

        await ws.prepare(request)

        await ws.send_str('hello')
        await ws.send_str('hello')
        ws.exception()

        await ws.send_str(WORD.STOP)

        return ws

    app = web.Application()
    app.router.add_route('GET', '/', handler)
    client = await aiohttp_client(app)

    ws = await client.ws_connect('/')

    await receive_message(ws)


async def test_websocket_close(loop, aiohttp_client) -> None:
    async def handler(request):
        ws = web.WebSocketResponse()
        if not ws.can_prepare(request):
            return web.HTTPUpgradeRequired()

        await ws.prepare(request)

        await ws.send_str('hello')
        await ws.close()

        return ws

    app = web.Application()
    app.router.add_route('GET', '/', handler)
    client = await aiohttp_client(app)

    ws = await client.ws_connect('/')

    await receive_message(ws)


async def test_websocket_send(loop, aiohttp_client, mock_to_thread_input) -> None:
    async def handler(request):
        ws = web.WebSocketResponse()
        if not ws.can_prepare(request):
            return web.HTTPUpgradeRequired()

        await ws.prepare(request)

        await ws.receive()
        await ws.receive()

        await ws.close()
        return ws

    app = web.Application()
    app.router.add_route('GET', '/', handler)
    client = await aiohttp_client(app)

    ws = await client.ws_connect('/')
    mock_to_thread_input.side_effect = ['hello', WORD.STOP]

    await send_message(ws)
