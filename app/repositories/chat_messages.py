from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


class ChatMessagesRepository:
    """Data-access layer for the chat_messages table."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_message(self, user_id: int, role: str, content: str) -> ChatMessage:
        message = ChatMessage(user_id=user_id, role=role, content=content)
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message

    async def get_recent_messages(self, user_id: int, limit: int) -> list[ChatMessage]:
        if limit <= 0:
            return []
        result = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

    async def get_all_messages(self, user_id: int) -> list[ChatMessage]:
        result = await self._session.execute(
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars().all())

    async def delete_history(self, user_id: int) -> None:
        await self._session.execute(delete(ChatMessage).where(ChatMessage.user_id == user_id))
        await self._session.commit()
