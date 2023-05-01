from datetime import datetime
from typing import Optional, List, Annotated

from fastapi import APIRouter, status, Depends, HTTPException, Response, Query
from sqlalchemy import select, insert, update, delete, func, or_
from sqlalchemy.dialects.postgresql import array_agg
from databases import Database

from app.dependencies import get_db
from app.models import MenuItem, MenuCategory
from app.schemas.menu_item import (
    MenuItemCreateSchema,
    MenuItemResponse,
    MenuItemUpdateSchema,
    MenuItemResponseSchema,
    ListMenuItemResponse,
    MenuItemFilterResponse
)
from app.oauth2 import get_auth_user_by_token

router = APIRouter(
    prefix="/api/menu-items",
    tags=["menu-items"],
    dependencies=[Depends(get_auth_user_by_token)]
)

async def get_menu_item_or_404(menu_item_id: int) -> MenuItem:
    database = get_db()
    query = select(MenuItem).where(MenuItem.id == menu_item_id)
    exists_item = await database.fetch_one(query)
    if not exists_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No event with id: {menu_item_id}")

    return exists_item


def get_order(order: str):
    order_map = {
    }
    return order_map.get(order)


@router.get("/filters")
async def get_menu_items_filter(database: Database = Depends(get_db)) -> List[MenuItemFilterResponse]:
    filter_query = select(
        MenuItem.category, array_agg(func.distinct(MenuItem.sub_category)).label("sub_categories")
    ).group_by(MenuItem.category)
    result = await database.fetch_all(filter_query)
    return [MenuItemFilterResponse.from_orm(category) for category in result]


@router.get("/", response_model=ListMenuItemResponse)
async def get_menu_items(
        database: Database = Depends(get_db),
        limit: int = 10,
        page: int = 1,
        category: Annotated[List[MenuCategory], Query()] = [],
        sub_category: Annotated[List[str], Query()] = []
):
    query = select(MenuItem).where(or_(
        or_(MenuItem.category == c.value for c in category),
        or_(MenuItem.sub_category == sub_c for sub_c in sub_category)
    ))
    skip = (page - 1) * limit
    query = query.limit(limit).offset(skip)

    reservations = await database.fetch_all(query=query)
    all_reservations_query = select(
        func.count()
    ).select_from(
        select(MenuItem).where(or_(
        or_(MenuItem.category == c.value for c in category),
        or_(MenuItem.sub_category == sub_c for sub_c in sub_category)
    )))
    result_count = await database.fetch_val(all_reservations_query) or 0
    return {"status": "success", "results": result_count, "menu_items": reservations}


@router.get("/{menu_item_id}")
async def get_one_menu_item(menu_item: MenuItem = Depends(get_menu_item_or_404)) -> MenuItemResponse:
    return MenuItemResponse(status="success", menu_item=menu_item)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=MenuItemResponse)
async def create_menu_item(payload: MenuItemCreateSchema, database: Database = Depends(get_db)) -> MenuItemResponse:
    query = insert(MenuItem).values(**payload.dict())
    event_id = await database.execute(query=query)
    return MenuItemResponse(status="success", menu_item=MenuItemResponseSchema(id=event_id, **payload.dict()))


@router.patch("/{menu_item_id}")
async def update_menu_item(payload: MenuItemUpdateSchema,
                           menu_item: MenuItem = Depends(get_menu_item_or_404),
                           database: Database = Depends(get_db)) -> MenuItemResponse:
    data = payload.dict(exclude_unset=True)
    update_query = update(MenuItem).where(MenuItem.id == menu_item.id).values(updatedAt=datetime.now(), **data)
    await database.execute(update_query)
    result = await database.fetch_one(select(MenuItem).where(MenuItem.id == menu_item.id))

    return MenuItemResponse(status="success", menu_item=result)


@router.delete("/{menu_item_id}")
async def delete_menu_item(menu_item: MenuItem = Depends(get_menu_item_or_404), database: Database = Depends(get_db)):
    delete_query = delete(MenuItem).where(MenuItem.id == menu_item.id)
    await database.execute(delete_query)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
