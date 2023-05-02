from fastapi import APIRouter, status, Depends, Response

from app.dependencies import upload_file_with_directory
from app.schemas.user import UserListResponse, CreateUser, UserResponse, BaseUser, UpdateUser
from app.oauth2 import get_auth_user_by_token
from app.service_layer.users_service import (
    add_avatar_for_user,
    create_new_user,
    delete_existed_user,
    get_list_users,
    get_count_of_list_users,
    update_existed_user
)


router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    dependencies=[Depends(get_auth_user_by_token)]
)

upload_user_file = upload_file_with_directory("users")


@router.get("/")
async def get_all_users(users = Depends(get_list_users), count = Depends(get_count_of_list_users)) -> UserListResponse:
    return UserListResponse(status="success", result=count, users=users)


@router.post("/")
async def create_user(payload: CreateUser) -> UserResponse:
    user_data = await create_new_user(payload.dict())
    return UserResponse(status="success", user=BaseUser(**user_data))


@router.patch("/{user_id}")
async def update_user(payload: UpdateUser, user_id: int) -> UserResponse:
    updated_user = await update_existed_user(user_id, payload.dict(exclude_unset=True))
    return UserResponse(status="success", user=BaseUser.from_orm(updated_user))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    await delete_existed_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{user_id}/upload-image", status_code=status.HTTP_201_CREATED)
async def upload_image(user_id: int, upload_file_name: str = Depends(upload_user_file), ):
    await add_avatar_for_user(user_id, upload_file_name)
    return Response(status_code=status.HTTP_201_CREATED)