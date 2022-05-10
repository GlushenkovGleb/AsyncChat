# type: ignore
import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.service.crud import ChatCrud


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


@pytest.fixture
def mock_handler(mocker):
    return mocker.patch('app.api.rest.ChatCrud')


def test_api_register(redis_client, mock_handler, mocker):
    # prepare
    handler = ChatCrud(redis_client)
    handler.register_user = MagicMock(return_value=async_return(1))
    mock_handler.connect_handler.return_value = async_return(handler)

    from app.app import app

    client = TestClient(app)

    response = client.post('/users', json={'name': 'user'})
    mock_handler.connect_handler.assert_called_once_with()
    handler.register_user.assert_called_once_with('user')
    assert response.json() == {'id': 1}


def test_api_get_latest(redis_client, mock_handler):
    # prepare
    handler = ChatCrud(redis_client)
    handler.load_messages = MagicMock(return_value=async_return(['message']))
    mock_handler.connect_handler.return_value = async_return(handler)

    from app.app import app

    client = TestClient(app)

    response = client.get('/messages')
    mock_handler.connect_handler.assert_called_once_with()
    handler.load_messages.assert_called_once_with()
    assert response.json() == ['message']
