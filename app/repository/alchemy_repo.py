from datetime import datetime

from abc import ABC, abstractmethod
from sqlalchemy import select, func, insert, update, delete
from app.dependencies import get_db


class AbstractSimpleCrud(ABC):

    @abstractmethod
    def get_list(self):
        raise NotImplementedError

    @abstractmethod
    def get_instance(self, instance_id):
        raise NotImplementedError

    @abstractmethod
    def create_instance(self, data):
        raise NotImplementedError

    @abstractmethod
    def update_instance(self, instance_id, data):
        raise NotImplementedError

    @abstractmethod
    def delete_instance(self, instance_id):
        raise NotImplementedError


class SQLAlchemySimpleCRUDRepository(AbstractSimpleCrud):
    model = None

    def __init__(self):
        self.database = get_db()

    async def get_list(self, limit: int = 10, page: int = 1):
        skip = (page - 1) * limit
        query = select(self.model).limit(limit).offset(skip)
        instances = await self.database.fetch_all(query=query)
        return instances

    async def get_count_of_list(self):
        query_count = select(func.count()).select_from(select(self.model))
        count = await self.database.fetch_val(query_count)
        return count

    async def get_instance(self, instance_id: int):
        query = select(self.model).where(self.model.id == instance_id)
        instance = await self.database.fetch_one(query)
        return instance

    async def create_instance(self, data: dict):
        query = insert(self.model).values(**data)
        instance_id = await self.database.execute(query=query)
        return instance_id

    async def update_instance(self, instance_id, data: dict):
        update_query = update(self.model).where(self.model.id == instance_id).values(updatedAt=datetime.now(), **data)
        await self.database.execute(update_query)
        updated_instance = await self.database.fetch_one(select(self.model).where(self.model.id == instance_id))
        return updated_instance

    async def delete_instance(self, instance_id):
        delete_query = delete(self.model).where(self.model.id == instance_id)
        await self.database.execute(delete_query)
