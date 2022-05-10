import redis
from aioredis import Redis

from .settings import settings


async def get_redis() -> Redis:  # pragma: no cover
    redis_db = await Redis(
        host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
    )
    return redis_db


def init_db() -> None:  # pragma: no cover
    redis_db = redis.Redis(
        host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
    )
    redis_db.set('ID_COUNTER', 1)
    redis_db.delete('latest_messages')
    redis_db.close()
