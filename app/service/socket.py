from __future__ import annotations

import asyncio
import json
from typing import Optional

from aioredis import Redis
from fastapi import WebSocket, WebSocketDisconnect

from ..database import get_redis
from ..models import WORD, StopSocketTasks


class ChatClient:
    @staticmethod
    def get_user_key(user_id: str) -> str:  # pragma: no cover
        """Returns key for storing name, id - key, name - value"""
        return f'user_{user_id}:'

    @staticmethod
    def make_message_json(client_id: str, message: str) -> str:
        """Returns a json string for publishing"""
        message_dict = {'client_id': client_id, 'message': message}
        return json.dumps(message_dict)

    @staticmethod
    def make_user_message(name: str, text: str) -> str:  # pragma: no cover
        """Returns a message that will be sent to user's websocket"""
        return f'{name}: {text}'

    @staticmethod
    def get_message(client_id: str, notification: dict[str, str]) -> Optional[str]:
        """Returns a message from dict if message was not made by current user, else None"""
        if notification['type'] == 'subscribe':
            return None
        message_dict = json.loads(notification['data'])
        if message_dict['client_id'] == client_id:
            return None
        return message_dict['message']

    @classmethod
    async def connect_client(
        cls, client_id: str, websocket: WebSocket
    ) -> ChatClient:  # pragma: no cover
        """Returns a ChatClient instance, once connected to aioredis"""
        await websocket.accept()
        redis = await get_redis()
        return cls(client_id, websocket, redis)

    def __init__(self, client_id: str, websocket: WebSocket, redis: Redis):
        self.client_id = client_id
        self.websocket = websocket
        self.redis = redis

    async def start_chat(self) -> None:  # pragma: no cover
        """Handles loop operations for websockets"""
        name = await self.redis.get(self.get_user_key(self.client_id))

        tasks = [
            asyncio.ensure_future(coro) for coro in (self.publish(name), self.consume())
        ]
        try:
            await asyncio.gather(*tasks)
        except StopSocketTasks:
            for task in tasks:
                task.cancel()

    async def publish(self, name: str) -> None:
        """Receives a message from client,
        then makes a json string and publish it to redis"""
        while True:
            try:
                text = await self.websocket.receive_text()
                if text == WORD.STOP:
                    raise StopSocketTasks

                # make message
                user_message = self.make_user_message(name, text)
                message = self.make_message_json(self.client_id, user_message)

                await self.redis.publish('channel', message)
                await self.save_message(user_message)

            except WebSocketDisconnect:
                break

    async def consume(self) -> None:
        """Takes a json from channel,
        then converts it to message and sends it to user"""
        channel = self.redis.pubsub()
        await channel.subscribe(
            'channel',
        )
        try:
            async for notification in channel.listen():
                message = self.get_message(self.client_id, notification)
                if message == WORD.STOP:
                    break
                if message is not None:
                    await self.websocket.send_text(message)

        except WebSocketDisconnect:
            pass

    async def save_message(self, message: str) -> None:
        """Saves message to redis list latest_messages"""
        await self.redis.lpush('latest_messages', message)
        await self.redis.ltrim('latest_messages', 0, 49)
