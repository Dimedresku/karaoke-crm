from datetime import datetime

from sqlalchemy import select, func, update

from app.repository.alchemy_repo import SQLAlchemySimpleCRUDRepository
from app.models import User


class UsersRepository(SQLAlchemySimpleCRUDRepository):
    model = User

    async def get_list(self, limit: int = 10, page: int = 1, search=""):
        skip = (page - 1) * limit
        if search:
            query = select(self.model).where(self.model.name.ilike(f"%{search}%")).limit(limit).offset(skip)
        else:
            query = select(self.model).limit(limit).offset(skip)
        users = await self.database.fetch_all(query=query)
        return users

    async def get_count_of_list(self):
        query_count = select(func.count()).select_from(select(self.model))
        count = await self.database.fetch_val(query_count)
        return count

    async def update_avatar_for_user(self, user_id: int, avatar_name: str):
        update_query = update(self.model).where(self.model.id == user_id).values(
            avatar=f'/static/users/{avatar_name}',
            updatedAt=datetime.now()
        )
        await self.database.execute(update_query)


def user_repository_factory():
    return UsersRepository()
