import pytest

from app.service.crud import ChatCrud


@pytest.fixture()
def handler(redis_client):
    return ChatCrud(redis_client)


@pytest.fixture()
def mock_get_redis(mocker):
    return mocker.patch('app.service.crud.get_redis')


def test_get_user_key():
    user_key = ChatCrud.get_user_key(1)
    assert user_key == 'user_1:'


@pytest.mark.anyio
async def test_load_messages(redis_client, handler):
    # init db
    messages = ['message1', 'message2', 'message3']
    for message in messages:
        await redis_client.lpush('latest_messages', message)

    messages.reverse()
    assert await handler.load_messages() == messages


@pytest.mark.anyio
async def test_register_user(redis_client, handler):
    user_id = await handler.register_user('user')
    user_name = await redis_client.get(handler.get_user_key(user_id))

    assert user_id == 1
    assert user_name == 'user'


@pytest.mark.anyio
async def test_connect_handler(mock_get_redis):
    handler = await ChatCrud.connect_handler()

    await mock_get_redis.called_once_with()
    assert isinstance(handler, ChatCrud)
