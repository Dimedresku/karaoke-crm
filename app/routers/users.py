from datetime import datetime

from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from sqlalchemy import select, insert, update, delete, func
from databases import Database

from app.dependencies import get_db, upload_file_with_directory
from app.models import User
from app.schemas.user import UserListResponse, CreateUser, UserResponse, BaseUser, UpdateUser
from app.utils import get_hashed_password, delete_avatar
from app.oauth2 import get_auth_user_by_token


router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_auth_user_by_token)]
)

upload_user_file = upload_file_with_directory("users")


async def get_user_or_404(user_id: int) -> User:
    database = get_db()
    query = select(User).where(User.id == user_id)
    user = await database.fetch_one(query=query)
    if not user:
        raise HTTPException(status_code=404, detail="Not found")

    return user


@router.get("/")
async def get_all_users(
        database: Database = Depends(get_db),
        limit: int = 10,
        page: int = 1,
        search: str = "") -> UserListResponse:
    skip = (page - 1) * limit
    if search:
        query = select(User).where(User.name.ilike(f"%{search}%")).limit(limit).offset(skip)
    else:
        query = select(User).limit(limit).offset(skip)
    query_count = select(func.count()).select_from(select(User))
    users = await database.fetch_all(query=query)
    count = await database.fetch_val(query_count)
    return UserListResponse(status="success", result=count, users=users)


@router.post("/")
async def create_user(payload: CreateUser, database: Database = Depends(get_db)) -> UserResponse:
    payload.password = get_hashed_password(payload.password)
    query = insert(User).values(**payload.dict())
    user_id = await database.execute(query)
    return UserResponse(status="success", user=BaseUser(id=user_id, **payload.dict()))


@router.patch("/{user_id}")
async def update_user(payload: UpdateUser, user: User = Depends(get_user_or_404), database: Database = Depends(get_db)):
    data = payload.dict(exclude_unset=True)
    update_query = update(User).where(User.id == user.id).values(updatedAt=datetime.now(), **data)
    await database.execute(query=update_query)
    result = await database.fetch_one(select(User).where(User.id == user.id))
    return UserResponse(status="success", user=BaseUser.from_orm(result))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: User = Depends(get_user_or_404), database: Database = Depends(get_db)):
    count_query = select(func.count()).select_from(select(User))
    count = await database.execute(count_query)
    if count > 1:
        delete_avatar(user.avatar)
        query = delete(User).where(User.id == user.id)
        await database.execute(query=query)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{user_id}/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(user: User = Depends(get_user_or_404),
                       upload_file_name: str = Depends(upload_user_file),
                       database: Database = Depends(get_db)):

    update_query = update(User).where(User.id == user.id).values(
        avatar=f'/static/users/{upload_file_name}',
        updatedAt=datetime.now()
    )
    await database.execute(update_query)

    return Response(status_code=status.HTTP_201_CREATED)