from datetime import datetime, date, timedelta
from enum import Enum
from typing import List

from fastapi import status, HTTPException

from app.models import Reservations
from app.schemas.reservations import (
    ResponseReservation,
    ReservationCreateSchema,
    ReservationStatisticSchema,
    ReservationUpdateSchema,
    PeopleCountStatistic
)
from app.repository.reservation import reservations_repo_factory


def get_date_filter(date_from: date | None = None, date_to: date | None = None):
    if date_from:
        date_from = datetime.combine(date_from, datetime.min.time())
    if date_to:
        date_to = datetime.combine(date_to, datetime.max.time())
    return {"date_from": date_from, "date_to": date_to}


async def get_list_reservations(
        date_from: date | None = None,
        date_to: date | None = None,
        limit: int = 10,
        page: int = 1,
        order: str | None = None) -> List[ResponseReservation]:

    date_filters = get_date_filter(date_from, date_to)

    repository = reservations_repo_factory()
    reservations = await repository.get_list(
        limit=limit,
        page=page,
        date_from=date_filters.get("date_from"),
        date_to=date_filters.get("date_to"),
        order=order
    )
    return [ResponseReservation.from_orm(reservation) for reservation in reservations]


async def get_count_of_list_reservations(
        date_from: date | None = None,
        date_to: date | None = None) -> int:
    date_filters = get_date_filter(date_from, date_to)
    repository = reservations_repo_factory()
    result_count = await repository.get_count_of_list(
        date_from=date_filters.get("date_from"),
        date_to=date_filters.get("date_to"))

    return result_count


async def get_reservation_or_404(reservation_id: int) -> Reservations:
    repository = reservations_repo_factory()
    exists_reservation = await repository.get_instance(reservation_id)
    if not exists_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No event with id: {reservation_id}")

    return exists_reservation


async def create_new_reservation(data: ReservationCreateSchema) -> ResponseReservation:
    repository = reservations_repo_factory()
    reservation_id = await repository.create_instance(data.dict())
    return ResponseReservation(id=reservation_id, **data.dict())


async def update_exist_reservation(data: ReservationUpdateSchema, reservation_id: int) -> ResponseReservation:
    repository = reservations_repo_factory()
    updated_reservation = await repository.update_instance(reservation_id, data.dict(exclude_unset=True))
    return ResponseReservation.from_orm(updated_reservation)


async def delete_exist_reservation(reservation_id: int):
    repository = reservations_repo_factory()
    await repository.delete_instance(reservation_id)


class StatisticType(str, Enum):
    WEEK = 'week'
    MONTH = 'month'


async def get_reservations_count_statistics(statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:

    end_range = date.today()
    if statistic_type == StatisticType.WEEK:
        start_range = datetime.combine(end_range - timedelta(days=6), datetime.min.time())
    else:
        start_range = datetime.combine(end_range - timedelta(days=29), datetime.min.time())

    repository = reservations_repo_factory()
    reservations = await repository.get_reservations_count_for_period(start_range=start_range, end_range=end_range)
    statistics = [ReservationStatisticSchema.from_orm(reservation).dict() for reservation in reservations]
    return statistics


async def get_people_count_stat(statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:

    end_range = datetime.now()
    if statistic_type == StatisticType.WEEK:
        start_range = datetime.combine(end_range - timedelta(days=6), datetime.min.time())
    else:
        start_range = datetime.combine(end_range - timedelta(days=29), datetime.min.time())

    repository = reservations_repo_factory()
    reservations = await repository.get_people_count_tables_for_period(start_range=start_range, end_range=end_range)
    statistics = [PeopleCountStatistic.from_orm(reservation).dict() for reservation in reservations]
    return statistics
