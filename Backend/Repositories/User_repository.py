from sqlalchemy.ext.asyncio import AsyncSession
from Backend.Entities import User
from sqlalchemy.orm import class_mapper
from sqlalchemy import select, delete


class User_repository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, new_user: User) -> User:
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_name(self, name: str) -> User | None:
        stmt = select(User).where(User.username == name)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def delete_user_by_id(self, user_id: int) -> bool:
        stmt = delete(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0