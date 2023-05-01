from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

from app.models import MenuCategory

class ManuItemBaseSchema(BaseModel):
    category: MenuCategory
    sub_category: str
    name: str
    sub_name: str | None
    main_unit: str
    main_price: str
    secondary_unit: str | None
    secondary_price: str | None
    special: bool
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class MenuItemResponseSchema(ManuItemBaseSchema):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class MenuItemCreateSchema(BaseModel):
    category: MenuCategory
    sub_category: str
    name: str
    sub_name: str
    main_unit: str
    main_price: str
    secondary_unit: Optional[str]
    secondary_price: Optional[str]
    special: Optional[bool]
    createdAt: Optional[datetime] = Field(default_factory=datetime.now)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True


class MenuItemUpdateSchema(BaseModel):
    category: Optional[MenuCategory]
    sub_category: Optional[str]
    name: Optional[str]
    sub_name: Optional[str]
    main_unit: Optional[str]
    main_price: Optional[str]
    secondary_unit: Optional[str]
    secondary_price: Optional[str]
    special: Optional[bool]

    class Config:
        orm_mode = True


class ListMenuItemResponse(BaseModel):
    status: str
    results: int
    menu_items: List[MenuItemResponseSchema]


class MenuItemResponse(BaseModel):
    status: str
    menu_item: MenuItemResponseSchema


class MenuItemFilterResponse(BaseModel):
    category: str
    sub_categories: List[str]

    class Config:
        orm_mode=True