from enum import Enum
from datetime import timedelta, date
from sqlalchemy import select, func, case, cast, Integer
from typing import List

from app.models import Reservations
from app.schemas.reservations import ReservationStatisticSchema, PeopleCountStatistic


class StatisticType(str, Enum):
    WEEK = 'week'
    MONTH = 'month'


class ReservationStatistic:

    def __init__(self, db):
        self.db = db

    async def get_reservations_count_statistics(
            self, statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:
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

        reservations = await self.db.fetch_all(count_query)

        statistics = [ReservationStatisticSchema.from_orm(reservation).dict() for reservation in reservations]
        return statistics


    async def get_people_count_statistics(
            self, statistic_type: StatisticType = StatisticType.WEEK) -> List[dict]:
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

        reservations = await self.db.fetch_all(people_count)
        statistics = [PeopleCountStatistic.from_orm(reservation).dict() for reservation in reservations]
        return statistics

