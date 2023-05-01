from datetime import datetime, date, timedelta
from enum import Enum
from typing import List

from sqlalchemy import select, func, case, cast, Integer, insert, update, delete

from fastapi import status, HTTPException

from app.dependencies import get_db
from app.models import Reservations
from app.schemas.reservations import (
    ResponseReservation,
    ReservationCreateSchema,
    ReservationStatisticSchema,
    ReservationUpdateSchema,
    PeopleCountStatistic
)

def get_date_filter(date_from: date | None = None, date_to: date | None = None):
    if date_from:
        date_from = datetime.combine(date_from, datetime.min.time())
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


async def create_new_reservation(data: ReservationCreateSchema) -> ResponseReservation:
    database = get_db()
    query = insert(Reservations).values(**data.dict())
    reservation_id = await database.execute(query=query)
    return ResponseReservation(id=reservation_id, **data.dict())


async def update_exist_reservation(data: ReservationUpdateSchema, reservation_id: int) -> ResponseReservation:
    database = get_db()
    reservation = await get_reservation_or_404(reservation_id)
    data = data.dict(exclude_unset=True)
    update_query = update(Reservations).where(
        Reservations.id == reservation.id
    ).values(updatedAt=datetime.now(), **data)
    await database.execute(update_query)
    updated_reservation = await database.fetch_one(select(Reservations).where(Reservations.id == reservation.id))
    return ResponseReservation.from_orm(updated_reservation)


async def delete_exist_reservation(reservation_id: int):
    database = get_db()
    reservation = await get_reservation_or_404(reservation_id)
    if reservation:
        delete_query = delete(Reservations).where(Reservations.id == reservation.id)
        await database.execute(delete_query)


class StatisticType(str, Enum):
    WEEK = 'week'
    MONTH = 'month'


async def get_reservations_count_statistics(statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:
    database = get_db()

    end_range = date.today()
    if statistic_type == StatisticType.WEEK:
        start_range = end_range - timedelta(days=6)
    else:
        start_range = end_range - timedelta(days=29)

    day_date = func.date_trunc("day", Reservations.date_reservation).label("day_date")

    count_query = select(
        day_date,
        func.count(Reservations.id).label("reserved_count"),
        func.sum(case((Reservations.served == True, cast(1, Integer)), else_=cast(0, Integer))).label("served_count")
    ).group_by(
        "day_date"
    ).having(
        day_date.between(start_range, end_range)
    ).order_by("day_date")

    reservations = await database.fetch_all(count_query)

    statistics = [ReservationStatisticSchema.from_orm(reservation).dict() for reservation in reservations]
    return statistics


async def get_people_count_stat(statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:
    database = get_db()

    end_range = date.today()
    if statistic_type == StatisticType.WEEK:
        start_range = end_range - timedelta(days=6)
    else:
        start_range = end_range - timedelta(days=29)

    people_count = select(
        Reservations.people_count,
        func.count(Reservations.id).label("reservations_count")
    ).group_by(
        Reservations.people_count
    ).where(
        Reservations.date_reservation.between(start_range, end_range)
    ).order_by(
        Reservations.people_count
    )

    reservations = await database.fetch_all(people_count)
    statistics = [PeopleCountStatistic.from_orm(reservation).dict() for reservation in reservations]
    return statistics
