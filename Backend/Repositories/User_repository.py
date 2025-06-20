from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from Backend.Entities import User
from sqlalchemy.orm import class_mapper


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

    def as_dict(self):
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns}