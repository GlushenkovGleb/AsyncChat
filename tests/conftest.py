import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from app.app import app


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect('/ws') as websocket:
        data = websocket.receive_json()
        assert data == {'msg': 'Hello WebSocket'}


@pytest.fixture()
async def redis_client():
    redis_db = fakeredis.aioredis.FakeRedis(decode_responses=True)
    await redis_db.set('ID_COUNTER', 1)
    await redis_db.delete('latest_messages')
    yield redis_db
    await redis_db.flushall()
    await redis_db.close()
