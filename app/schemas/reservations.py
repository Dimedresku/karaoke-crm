from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class ReservationBaseSchema(BaseModel):
    date_reservation: datetime
    people_count: int
    phone_number: str
    email: Optional[str]
    comment: Optional[str]
    admin_comment: Optional[str]
    served: bool
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True


class ResponseReservation(ReservationBaseSchema):
    id: int

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ReservationCreateSchema(BaseModel):
    date_reservation: datetime
    people_count: int
    phone_number: str
    email: Optional[str]
    comment: Optional[str]
    admin_comment: Optional[str]
    served: bool = Field(default=False)

    class Config:
        orm_mode = True


class ReservationUpdateSchema(BaseModel):
    date_reservation: Optional[datetime]
    people_count: Optional[int]
    phone_number: Optional[str]
    email: Optional[str]
    comment: Optional[str]
    admin_comment: Optional[str]
    served: Optional[bool]

    class Config:
        orm_mode = True


class ListReservationsResponse(BaseModel):
    status: str
    results: str
    reservations: List[ReservationBaseSchema]


class ReservationResponse(BaseModel):
    status: str
    reservation: ResponseReservation


class ReservationStatisticSchema(BaseModel):
    day_date: date
    reserved_count: int
    served_count: int

    class Config:
        orm_mode = True


class PeopleCountStatistic(BaseModel):
    people_count: int
    reservations_count: int

    class Config:
        orm_mode = True
