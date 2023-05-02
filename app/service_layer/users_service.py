from typing import List

from fastapi import HTTPException, status

from app.repository.users import user_repository_factory
from app.schemas.user import BaseUser
from app.utils import get_hashed_password, delete_avatar
from app.models import User


async def get_user_or_404(user_id: int) -> User:
    repository = user_repository_factory()
    user = await repository.get_instance(instance_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return user


async def get_list_users(limit: int = 10, page: int = 1, search: str = "") -> List[BaseUser]:
    repository = user_repository_factory()
    users = await repository.get_list(limit, page, search)
    return users


async def get_count_of_list_users() -> int:
    repository = user_repository_factory()
    users_count = await repository.get_count_of_list()
    return users_count


async def create_new_user(data: dict) -> dict:
    data["password"] = get_hashed_password(data["password"])
    repository = user_repository_factory()
    user_id = await repository.create_instance(data)
    data.update(id=user_id)
    return data


async def update_existed_user(user_id: int, data: dict):
    repository = user_repository_factory()
    user = await get_user_or_404(user_id)
    updated_user = await repository.update_instance(instance_id=user.id, data=data)
    return updated_user


async def delete_existed_user(user_id: int):
    repository = user_repository_factory()
    user = await get_user_or_404(user_id)
    delete_avatar(user.avatar)
    await repository.delete_instance(instance_id=user.id)


async def add_avatar_for_user(user_id: int, file_name: str):
    repository = user_repository_factory()
    user = await repository.get_instance(instance_id=user_id)
    await repository.update_avatar_for_user(user_id=user.id, avatar_name=file_name)
