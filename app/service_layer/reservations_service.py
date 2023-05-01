from datetime import datetime, date
from typing import List

from sqlalchemy import select, insert, update, delete, func
from fastapi import status, HTTPException

from app.dependencies import get_db
from app.models import Reservations
from app.schemas.reservations import (
    ResponseReservation,
    ReservationCreateSchema
)

def get_date_filter(date_from: date | None = None, date_to: date | None = None):
    if date_from:
        date_from = datetime.combine(date_from, datetime.max.time())
    if date_to:
        date_to = datetime.combine(date_to, datetime.max.time())
    return {"date_from": date_from, "date_to": date_to}


def get_order(order: str):
    order_map = {
        "date_desc": Reservations.date_reservation.desc(),
        "date_asc": Reservations.date_reservation.asc(),
        "people_desc": Reservations.people_count.desc(),
        "people_asc": Reservations.people_count.asc(),
    }
    return order_map.get(order)


async def get_list_reservations(
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 10,
        page: int = 1,
        order: str | None = None) -> List[ResponseReservation]:
    database = get_db()

    skip = (page - 1) * limit
    date_filters = get_date_filter(date_from, date_to)

    query = select(Reservations).limit(limit).offset(skip)

    if order:
        order_rule = get_order(order)
        query = query.order_by(order_rule)
    if date_filters.get("date_from"):
        query = query.where(Reservations.date_reservation >= date_filters.get("date_from"))
    if date_filters.get("date_to"):
        query = query.where(Reservations.date_reservation <= date_filters.get("date_to"))
    reservations = await database.fetch_all(query=query)
    return [ResponseReservation.from_orm(reservation) for reservation in reservations]


async def get_count_of_list_reservations(
        date_from: date | None = None,
        date_to: date | None = None) -> int:
    database = get_db()

    date_filters = get_date_filter(date_from, date_to)

    count_query = select(Reservations)
    if date_filters.get("date_from"):
        count_query = count_query.where(Reservations.date_reservation >= date_filters.get("date_from"))
    if date_filters.get("date_to"):
        count_query = count_query.where(Reservations.date_reservation <= date_filters.get("date_to"))
    all_reservations_query = select(func.count()).select_from(count_query)
    result_count = await database.fetch_val(all_reservations_query) or 0
    return result_count


async def get_reservation_or_404(reservation_id: int) -> Reservations:
    database = get_db()
    query = select(Reservations).where(Reservations.id == reservation_id)
    exists_reservation = await database.fetch_one(query)
    if not exists_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No event with id: {reservation_id}")

    return exists_reservation


async def create_reservation(data: ReservationCreateSchema) -> ResponseReservation:
    query = insert(Reservations).values(**data.dict())
    reservation_id = await database.execute(query=query)
    return ResponseReservation(id=reservation_id, **data.dict())
