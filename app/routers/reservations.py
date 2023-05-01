from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy import select, insert, update, delete, func
from databases import Database
from typing import List

from app.dependencies import get_db
from app.models import Reservations
from app.schemas.reservations import (
    ReservationUpdateSchema,
    ReservationResponse,
    ResponseReservation,
    ReservationCreateSchema,
    ReservationStatisticSchema
)
from app.service_layer.reservations_service import (
    create_reservation,
    get_list_reservations,
    get_count_of_list_reservations,
    get_reservation_or_404
)
from app.oauth2 import get_auth_user_by_token
from app.service_layer.reservation_statistics import ReservationStatistic, StatisticType, PeopleCountStatistic

router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"],
    # dependencies=[Depends(get_auth_user_by_token)]
)


@router.get("/statistics")
async def get_reservations_statistics(type: StatisticType = StatisticType.WEEK.value,
                                      database: Database = Depends(get_db)) -> List[ReservationStatisticSchema]:
    service = ReservationStatistic(database)
    result = await service.get_reservations_count_statistics(type)
    return result


@router.get("/people_count_statistics")
async def get_reservations_statistics(type: StatisticType = StatisticType.WEEK.value,
                                      database: Database = Depends(get_db)) -> List[PeopleCountStatistic]:
    service = ReservationStatistic(database)
    result = await service.get_people_count_statistics(type)
    return result


@router.get("/")
async def get_reservations(
        result_count = Depends(get_count_of_list_reservations),
        reservations = Depends(get_list_reservations)
):
    return {"status": "success", "results": result_count, "reservations": reservations}


@router.get("/{reservation_id}")
async def get_one_reservation(reservation: Reservations = Depends(get_reservation_or_404)) -> ReservationResponse:
    return ReservationResponse(status="success", reservation=reservation)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ReservationResponse)
async def create_reservation(payload: ReservationCreateSchema) -> ReservationResponse:
    reservation = await create_reservation(payload)
    return ReservationResponse(status="success", reservation=reservation)


@router.patch("/{reservation_id}")
async def update_reservation(payload: ReservationUpdateSchema,
                       reservation: Reservations = Depends(get_reservation_or_404),
                       database: Database = Depends(get_db)) -> ReservationResponse:
    data = payload.dict(exclude_unset=True)
    update_query = update(Reservations).where(Reservations.id == reservation.id).values(updatedAt=datetime.now(), **data)
    await database.execute(update_query)
    result = await database.fetch_one(select(Reservations).where(Reservations.id == reservation.id))

    return ReservationResponse(status="success", reservation=result)


@router.delete("/{reservation_id}")
async def delete_reservation(reservation: Reservations = Depends(get_reservation_or_404), database: Database = Depends(get_db)):
    delete_query = delete(Reservations).where(Reservations.id == reservation.id)
    await database.execute(delete_query)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
