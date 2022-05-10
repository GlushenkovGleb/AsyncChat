import json
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from app.models import WORD, StopSocketTasks
from app.service.socket import ChatClient


def test_publish_ok(redis_client):
    async def app(scope, receive, send):
        # prepare
        assert scope['type'] == 'websocket'
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()

        chat = ChatClient('1', websocket, redis_client)
        with pytest.raises(StopSocketTasks) as exc_info:
            await chat.publish('user')

        assert 'StopSocketTasks' in str(exc_info)
        await websocket.close()

    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_text('hello')
        websocket.send_text(':quit')
        websocket.close()


def test_publish_close_connection(redis_client):
    async def app(scope, receive, send):
        # prepare
        assert scope['type'] == 'websocket'
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()

        chat = ChatClient('1', websocket, redis_client)
        await chat.publish('user')

        await websocket.close()

    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.send_text('hello')
        websocket.close()


@pytest.fixture()
def mock_pubsub(mocker):
    return mocker.patch('app.service.socket')


def test_consume(redis_client):
    async def app(scope, receive, send):
        # prepare socket
        assert scope['type'] == 'websocket'
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()

        # prepare channel
        msg_stop = {
            'type': 'something',
            'data': json.dumps({'client_id': '2', 'message': WORD.STOP}),
        }

        my_pubsub = redis_client.pubsub()
        my_pubsub.handle_message = MagicMock()
        my_pubsub.handle_message.side_effect = [msg_stop]
        redis_client.pubsub = MagicMock()
        redis_client.pubsub.return_value = my_pubsub

        chat = ChatClient('1', websocket, redis_client)
        await chat.consume()

        await websocket.close()

    client = TestClient(app)
    with client.websocket_connect('/') as websocket:
        websocket.close()


@pytest.mark.parametrize(
    'client_id, notification, expected',
    (
        (
            '1',
            {
                'type': 'subscribe',
                'data': json.dumps({'client_id': '1', 'message': 'message'}),
            },
            None,
        ),
        (
            '1',
            {
                'type': 'something',
                'data': json.dumps({'client_id': '1', 'message': 'message'}),
            },
            None,
        ),
        (
            '1',
            {
                'type': 'subscribe',
                'data': json.dumps({'client_id': '2', 'message': 'message'}),
            },
            None,
        ),
        (
            '1',
            {
                'type': 'something',
                'data': json.dumps({'client_id': '2', 'message': 'message'}),
            },
            'message',
        ),
    ),
)
def test_get_message(client_id, notification, expected):
    assert ChatClient.get_message(client_id, notification) == expected
