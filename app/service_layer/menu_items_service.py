from typing import Annotated, List

from fastapi import Query

from app.models import MenuItem, MenuCategory
from app.repository.menu_items import menu_items_repository_factory


async def get_menu_item_or_404(menu_item_id: int) -> MenuItem:
    repository = menu_items_repository_factory()
    exists_item = await repository.get_instance(instance_id=menu_item_id)
    if not exists_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No event with id: {menu_item_id}")

    return exists_item


async def get_list_menu_items(
        limit: int = 10,
        page: int = 1,
        category: Annotated[List[MenuCategory], Query()] = [],
        sub_category: Annotated[List[str], Query()] = []
):
    repository = menu_items_repository_factory()
    category_values = [cat.value for cat in category]
    menu_items = await repository.get_list(
        limit=limit, page=page, category=category_values, sub_category=sub_category)
    return menu_items


async def get_list_menu_items_count(
        category: Annotated[List[MenuCategory], Query()] = [],
        sub_category: Annotated[List[str], Query()] = []
):
    repository = menu_items_repository_factory()
    category_values = [cat.value for cat in category]
    items_count = await repository.get_count_of_list(category=category_values, sub_category=sub_category)
    return items_count


async def create_new_menu_item(data: dict):
    repository = menu_items_repository_factory()
    new_item_id = await repository.create_instance(data)
    data.update(id=new_item_id)
    return data


async def update_existed_item(menu_item_id: int, data: dict):
    repository = menu_items_repository_factory()
    menu_item = await get_menu_item_or_404(menu_item_id)
    updated_item = await repository.update_instance(instance_id=menu_item.id, data=data)
    return updated_item


async def delete_existed_item(menu_item_id: int):
    repository = menu_items_repository_factory()
    menu_item = await get_menu_item_or_404(menu_item_id)
    await repository.delete_instance(instance_id=menu_item.id)


async def get_filter_data():
    repository = menu_items_repository_factory()
    categories = await repository.get_category_with_subcategory()
    return categories