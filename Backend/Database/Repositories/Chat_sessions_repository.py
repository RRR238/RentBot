from sqlalchemy.ext.asyncio import AsyncSession
from Backend.Database.Entity_registration import Chat_session, Chat_history
from sqlalchemy import update
from sqlalchemy.sql import func, select,and_, delete
from datetime import datetime, timedelta


class Chat_session_repository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat_session(self,
                                  new_session:Chat_session) -> int:
        self.db.add(new_session)
        await self.db.commit()
        await self.db.refresh(new_session)
        return new_session.id

    async def add_new_message(self,
                              new_message:Chat_history)-> int:
        self.db.add(new_message)
        await self.db.commit()
        await self.db.refresh(new_message)
        return new_message.id

    async def update_last_interaction(self, session_id: int):
        stmt = (
            update(Chat_session)
            .where(Chat_session.id == session_id)
            .values(last_interaction=func.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def is_session_active_by_session_id(self, session_id: int) -> bool:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        stmt = (
            select(Chat_session.id)
            .where(
                Chat_session.id == session_id,
                Chat_session.last_interaction >= one_hour_ago,
                Chat_session.is_active == True
            )
        )

        result = await self.db.execute(stmt)
        return result.scalar() is not None

    async def get_active_session_by_user_id(self, user_id: int)-> int|None:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        session_stmt = (
            select(Chat_session.id)
            .where(
                Chat_session.user_id == user_id,
                Chat_session.last_interaction >= one_hour_ago,
                Chat_session.is_active == True
            )
            .limit(1)
        )
        session_result = await self.db.execute(session_stmt)
        session_id = session_result.scalar_one_or_none()
        return session_id

    async def get_active_chat_history(self, session_id: int)->list[dict]:

        # Fetch chat history for the found session_id
        history_stmt = (
            select(Chat_history.role, Chat_history.message)
            .where(Chat_history.session_id == session_id)
            .order_by(Chat_history.created_at.asc())
        )
        history_result = await self.db.execute(history_stmt)
        rows = history_result.all()

        return [{"role": role, "message": message} for role, message in rows]

    async def delete_chat_session_by_session_id(self, session_id: int):
        # Delete the chat session only
        await self.db.execute(
            delete(Chat_session).where(Chat_session.id == session_id)
        )
        await self.db.commit()

    async def mark_session_inactive_by_session_id(self, session_id: int):
        stmt = (
            update(Chat_session)
            .where(Chat_session.id == session_id)
            .values(is_active=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def mark_all_sessions_inactive_by_user(self, user_id: int):
        stmt = (
            update(Chat_session)
            .where(Chat_session.user_id == user_id)
            .values(is_active=False)
        )
        await self.db.execute(stmt)
        await self.db.commit()
