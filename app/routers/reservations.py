from fastapi import APIRouter, status, Depends, Response
from typing import List

from app.models import Reservations
from app.schemas.reservations import (
    ReservationUpdateSchema,
    ReservationResponse,
    ReservationCreateSchema,
    ReservationStatisticSchema,
    PeopleCountStatistic
)
from app.service_layer.reservations_service import (
    create_new_reservation,
    delete_exist_reservation,
    get_count_of_list_reservations,
    get_list_reservations,
    get_people_count_stat,
    get_reservation_or_404,
    get_reservations_count_statistics,
    update_exist_reservation,
    StatisticType
)
from app.oauth2 import get_auth_user_by_token

router = APIRouter(
    prefix="/api/reservations",
    tags=["reservations"],
    dependencies=[Depends(get_auth_user_by_token)]
)


@router.get("/statistics")
async def get_reservations_statistics(
        type: StatisticType = StatisticType.WEEK.value
) -> List[ReservationStatisticSchema]:
    result = await get_reservations_count_statistics(type)
    return result


@router.get("/people_count_statistics")
async def get_people_count_statistics(type: StatisticType = StatisticType.WEEK.value) -> List[PeopleCountStatistic]:
    result = await get_people_count_stat(type)
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
    reservation = await create_new_reservation(payload)
    return ReservationResponse(status="success", reservation=reservation)


@router.patch("/{reservation_id}")
async def update_reservation(reservation_id: int, payload: ReservationUpdateSchema) -> ReservationResponse:
    updated_reservation = await update_exist_reservation(payload, reservation_id)
    return ReservationResponse(status="success", reservation=updated_reservation)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reservation(reservation_id: int):
    await delete_exist_reservation(reservation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
