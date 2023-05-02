from datetime import datetime

from sqlalchemy import select, func, case, cast, Integer

from app.repository.alchemy_repo import SQLAlchemySimpleCRUDRepository
from app.models import Reservations


def get_order(order: str):
    order_map = {
        "date_desc": Reservations.date_reservation.desc(),
        "date_asc": Reservations.date_reservation.asc(),
        "people_desc": Reservations.people_count.desc(),
        "people_asc": Reservations.people_count.asc(),
    }
    return order_map.get(order)


class ReservationRepository(SQLAlchemySimpleCRUDRepository):
    model = Reservations

    async def get_list(self,
                 limit: int = 10,
                 page: int = 1,
                 date_from: datetime | None = None,
                 date_to: datetime | None = None,
                 order: str | None = None
) -> list:
        skip = (page - 1) * limit
        query = select(self.model).limit(limit).offset(skip)
        order_rule = get_order(order)
        if order_rule is not None:
            query = query.order_by(order_rule)
        if date_from:
            query = query.where(self.model.date_reservation >= date_from)
        if date_to:
            query = query.where(self.model.date_reservation <= date_to)
        reservations = await self.database.fetch_all(query=query)

        return reservations

    async def get_count_of_list(self,
                          date_from: datetime | None = None,
                          date_to: datetime | None = None,
) -> int:
        count_query = select(Reservations)
        if date_from:
            count_query = count_query.where(self.model.date_reservation >= date_from)
        if date_to:
            count_query = count_query.where(self.model.date_reservation <= date_to)
        all_reservations_query = select(func.count()).select_from(count_query)
        result_count = await self.database.fetch_val(all_reservations_query) or 0
        return result_count

    async def get_reservations_count_for_period(self, start_range: datetime, end_range: datetime):
        day_date = func.date_trunc("day", self.model.date_reservation).label("day_date")

        count_query = select(
            day_date,
            func.count(self.model.id).label("reserved_count"),
            func.sum(case((self.model.served == True, cast(1, Integer)), else_=cast(0, Integer))).label(
                "served_count")
        ).group_by(
            "day_date"
        ).having(
            day_date.between(start_range, end_range)
        ).order_by("day_date")

        reservations = await self.database.fetch_all(count_query)
        return reservations

    async def get_people_count_tables_for_period(self, start_range: datetime, end_range: datetime):
        people_count = select(
            self.model.people_count,
            func.count(self.model.id).label("reservations_count")
        ).group_by(
            self.model.people_count
        ).where(
            self.model.date_reservation.between(start_range, end_range)
        ).order_by(
            self.model.people_count
        )

        reservations = await self.database.fetch_all(people_count)

        return reservations


def reservations_repo_factory():
    return ReservationRepository()

