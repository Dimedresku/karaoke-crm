from typing import List

from fastapi import APIRouter, status, Depends, Response

from app.models import MenuItem
from app.schemas.menu_item import (
    MenuItemCreateSchema,
    MenuItemResponse,
    MenuItemUpdateSchema,
    MenuItemResponseSchema,
    ListMenuItemResponse,
    MenuItemFilterResponse
)
from app.oauth2 import get_auth_user_by_token
from app.service_layer.menu_items_service import (
    create_new_menu_item,
    delete_existed_item,
    get_filter_data,
    get_list_menu_items,
    get_list_menu_items_count,
    get_menu_item_or_404,
    update_existed_item
)

router = APIRouter(
    prefix="/api/menu-items",
    tags=["menu-items"],
    dependencies=[Depends(get_auth_user_by_token)]
)


@router.get("/filters")
async def get_menu_items_filter() -> List[MenuItemFilterResponse]:
    result = await get_filter_data()
    return [MenuItemFilterResponse.from_orm(category) for category in result]


@router.get("/", response_model=ListMenuItemResponse)
async def get_menu_items(
        menu_items = Depends(get_list_menu_items),
        result_count = Depends(get_list_menu_items_count)
):
    result_items = [MenuItemResponseSchema.from_orm(item) for item in menu_items]
    return {"status": "success", "results": result_count, "menu_items": result_items}


@router.get("/{menu_item_id}")
async def get_one_menu_item(menu_item: MenuItem = Depends(get_menu_item_or_404)) -> MenuItemResponse:
    return MenuItemResponse(status="success", menu_item=menu_item)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=MenuItemResponse)
async def create_menu_item(payload: MenuItemCreateSchema) -> MenuItemResponse:
    new_item_data = await create_new_menu_item(payload.dict())
    return MenuItemResponse(status="success", menu_item=MenuItemResponseSchema(**new_item_data))


@router.patch("/{menu_item_id}")
async def update_menu_item(payload: MenuItemUpdateSchema, menu_item_id: int) -> MenuItemResponse:
    menu_item = await update_existed_item(menu_item_id=menu_item_id, data=payload.dict(exclude_unset=True))
    return MenuItemResponse(status="success", menu_item=menu_item)


@router.delete("/{menu_item_id}")
async def delete_menu_item(menu_item_id: int):
    await delete_existed_item(menu_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
