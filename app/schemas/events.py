from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class EventBaseSchema(BaseModel):
    name: str
    description: str
    published: bool = True
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    image: str | None = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

class ResponseEvent(EventBaseSchema):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class EventUpdateSchema(BaseModel):
    name: Optional[str]
    description: Optional[str]
    published: Optional[bool] = True

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ListEventsResponse(BaseModel):
    status: str
    results: str
    events: List[EventBaseSchema]


class EventResponse(BaseModel):
    status: str
    event: ResponseEvent

