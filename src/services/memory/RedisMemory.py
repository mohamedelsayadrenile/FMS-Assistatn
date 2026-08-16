from __future__ import annotations

from datetime import UTC, datetime
import logging
from typing import Literal

from pydantic import BaseModel
from redis.asyncio import Redis


logger = logging.getLogger(__name__)

MessageRole = Literal["user", "assistant"]


class ConversationMessage(BaseModel):
    role: MessageRole
    content: str
    created_at: str


class RedisMemory:
    def __init__(self, redis_url: str, message_limit: int = 12, ttl_seconds: int = 3600) -> None:
        self.message_limit = message_limit
        self.ttl_seconds = ttl_seconds
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    async def get_messages(self, conversation_id: str) -> list[ConversationMessage]:
        key = self._conversation_key(conversation_id)
        logger.info("Loading conversation memory", extra={"conversation_id": conversation_id})
        try:
            raw_messages = await self.redis.lrange(key, 0, -1)
        except Exception:
            logger.exception("Failed to load conversation memory", extra={"conversation_id": conversation_id})
            raise

        messages: list[ConversationMessage] = []

        for raw_message in raw_messages:
            try:
                messages.append(ConversationMessage.model_validate_json(raw_message))
            except ValueError:
                logger.warning("Skipping invalid conversation memory item", extra={"conversation_id": conversation_id})

        logger.info(
            "Conversation memory loaded",
            extra={"conversation_id": conversation_id, "message_count": len(messages)},
        )
        return messages

    async def add_exchange(self, conversation_id: str, user_message: str, assistant_message: str) -> None:
        key = self._conversation_key(conversation_id)
        user_memory = self._build_message("user", user_message)
        assistant_memory = self._build_message("assistant", assistant_message)

        try:
            async with self.redis.pipeline(transaction=True) as pipe:
                pipe.rpush(key, user_memory.model_dump_json(), assistant_memory.model_dump_json())
                pipe.ltrim(key, -self.message_limit, -1)
                pipe.expire(key, self.ttl_seconds)
                await pipe.execute()
        except Exception:
            logger.exception("Failed to save conversation memory exchange", extra={"conversation_id": conversation_id})
            raise

        logger.info(
            "Conversation memory exchange saved",
            extra={
                "conversation_id": conversation_id,
                "message_limit": self.message_limit,
                "ttl_seconds": self.ttl_seconds,
            },
        )

    async def format_history(self, conversation_id: str) -> str:
        messages = await self.get_messages(conversation_id)
        if not messages:
            return "No previous messages."

        return "\n".join(f"{message.role}: {message.content}" for message in messages)

    async def close(self) -> None:
        logger.info("Closing Redis memory connection")
        await self.redis.aclose()

    def _conversation_key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}:messages"

    def _build_message(self, role: MessageRole, content: str) -> ConversationMessage:
        return ConversationMessage(
            role=role,
            content=content,
            created_at=datetime.now(UTC).isoformat(),
        )
