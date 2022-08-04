from __future__ import annotations

from typing import List

from aioredis import Redis

from ..database import get_redis


class ChatCrud:
    @staticmethod
    def get_user_key(user_id: int) -> str:
        """Returns key for user_name, id - key, name - value"""
        return f'user_{user_id}:'

    @classmethod
    async def connect_handler(cls) -> ChatCrud:
        """Return ChatCrud instance, once connected to aioredis"""
        redis = await get_redis()
        return cls(redis)

    def __init__(self, redis: Redis):
        self.redis = redis

    async def register_user(self, name: str) -> int:
        """Register user to redis, returns for of new user"""
        user_id = await self.redis.get('ID_COUNTER')
        if user_id is None:
            user_id = 0
        else:
            user_id = int(user_id)

        await self.redis.incr('ID_COUNTER')

        user_key = self.get_user_key(user_id)
        await self.redis.set(user_key, name)

        return user_id

    async def load_messages(self) -> List[str]:
        """Returns list of latest messages"""
        messages = await self.redis.lrange('latest_messages', 0, 49)
        return messages
