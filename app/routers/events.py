from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy import select, insert, update, delete, func
from databases import Database

from app.dependencies import get_db, upload_file_with_directory
from app.models import Events
from app.schemas.events import EventBaseSchema, EventUpdateSchema, EventResponse, ResponseEvent
from app.oauth2 import get_auth_user_by_token

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
    dependencies=[Depends(get_auth_user_by_token)]
)


upload_events_file = upload_file_with_directory("events")


async def get_event_or_404(event_id: int) -> Events:
    database = get_db()
    query = select(Events).where(Events.id == event_id)
    exists_event = await database.fetch_one(query)
    if not exists_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No event with id: {event_id}")

    return exists_event


@router.get("/")
async def get_events(database: Database = Depends(get_db), limit: int = 10, page: int = 1, search: str = ""):
    skip = (page - 1) * limit
    query = select(Events).where(Events.name.ilike(f"%{search}%")).limit(limit).offset(skip)
    events = await database.fetch_all(query=query)
    query_count = select(func.count()).select_from(select(Events))
    count = await database.fetch_val(query_count)

    return {"status": "success", "results": count, "events": events}


@router.get("/{event_id}")
async def get_one_event(event: Events = Depends(get_event_or_404)) -> EventResponse:
    return EventResponse(status="success", event=event)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=EventResponse)
async def create_event(payload: EventUpdateSchema, database: Database = Depends(get_db)) -> EventResponse:
    query = insert(Events).values(**payload.dict())
    event_id = await database.execute(query=query)
    return EventResponse(status="success", event=ResponseEvent(id=event_id, **payload.dict()))


@router.patch("/{event_id}")
async def update_event(payload: EventUpdateSchema,
                       event: Events = Depends(get_event_or_404),
                       database: Database = Depends(get_db)) -> EventResponse:
    data = payload.dict(exclude_unset=True)
    update_query = update(Events).where(Events.id == event.id).values(updatedAt=datetime.now(), **data)
    await database.execute(update_query)
    result = await database.fetch_one(select(Events).where(Events.id == event.id))

    return EventResponse(status="success", event=result)


@router.delete("/{event_id}")
async def delete_event(event: Events = Depends(get_event_or_404), database: Database = Depends(get_db)):
    delete_query = delete(Events).where(Events.id == event.id)
    await database.execute(delete_query)

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{event_id}/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(event: Events = Depends(get_event_or_404),
                       upload_file_name: str = Depends(upload_events_file),
                       database: Database = Depends(get_db)):

    update_query = update(Events).where(Events.id == event.id).values(
        image=f'/static/events/{upload_file_name}',
        updatedAt=datetime.now()
    )
    await database.execute(update_query)

    return Response(status_code=status.HTTP_201_CREATED)