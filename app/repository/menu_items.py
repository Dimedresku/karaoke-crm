from typing import List

from sqlalchemy import select, func, or_
from sqlalchemy.dialects.postgresql import array_agg

from app.repository.alchemy_repo import SQLAlchemySimpleCRUDRepository
from app.models import MenuItem


class MenuItemRepository(SQLAlchemySimpleCRUDRepository):
    model = MenuItem

    async def get_list(self,
                       limit: int = 10,
                       page: int = 1,
                       category: List[str] = [],
                       sub_category: List[str] = []
                       ):

        query = select(self.model).where(or_(
            or_(self.model.category == cat for cat in category),
            or_(self.model.sub_category == sub_cat for sub_cat in sub_category)
        ))
        skip = (page - 1) * limit
        query = query.limit(limit).offset(skip)

        reservations = await self.database.fetch_all(query=query)
        return reservations

    async def get_count_of_list(self,
                                category: List[str] = [],
                                sub_category: List[str] = []):
        count_query = select(
            func.count()
        ).select_from(
            select(self.model).where(or_(
                or_(self.model.category == cat for cat in category),
                or_(self.model.sub_category == sub_cat for sub_cat in sub_category)
            )))
        result_count = await self.database.fetch_val(count_query) or 0
        return result_count

    async def get_category_with_subcategory(self):
        filter_query = select(
            self.model.category, array_agg(func.distinct(self.model.sub_category)).label("sub_categories")
        ).group_by(self.model.category)
        result = await self.database.fetch_all(filter_query)
        return result


def menu_items_repository_factory():
    return MenuItemRepository()
