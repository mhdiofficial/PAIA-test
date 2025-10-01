from collections.abc import Sequence

from sqlalchemy import desc, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import ConversationMessage, MessageRole


settings = get_settings()


class MemoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_message(self, user_id: str, role: MessageRole, content: str) -> None:
        message = ConversationMessage(user_id=user_id, role=role, content=content)
        self.session.add(message)
        await self.session.commit()

    async def fetch_history(self, user_id: str) -> Sequence[ConversationMessage]:
        stmt = (
            select(ConversationMessage)
            .where(ConversationMessage.user_id == user_id)
            .order_by(desc(ConversationMessage.created_at))
            .limit(settings.max_history_messages)
        )
        result = await self.session.execute(stmt)
        records = list(result.scalars().all())
        records.reverse()
        return records

    async def prune_history(self, user_id: str, max_messages: int | None = None) -> None:
        """Ensure only the most recent messages are kept."""
        max_messages = max_messages or settings.max_history_messages
        stmt = (
            select(ConversationMessage.id)
            .where(ConversationMessage.user_id == user_id)
            .order_by(desc(ConversationMessage.created_at))
        )
        result = await self.session.execute(stmt)
        ids = result.scalars().all()
        excess = len(ids) - max_messages
        if excess <= 0:
            return
        ids_to_delete = ids[max_messages:]
        if not ids_to_delete:
            return
        await self.session.execute(
            delete(ConversationMessage).where(ConversationMessage.id.in_(ids_to_delete))
        )
        await self.session.commit()
