from pydantic import BaseModel
from typing import List, Optional

class BaseUser(BaseModel):
    id: int
    name: str | None
    username: str
    avatar: str | None

    class Config:
        orm_mode = True


class CreateUser(BaseModel):
    name: str | None
    username: str
    password: str
    avatar: str | None


class UpdateUser(BaseModel):
    name: Optional[str]
    username: Optional[str]


class UserListResponse(BaseModel):
    status: str
    result: int
    users: List[BaseUser]


class UserResponse(BaseModel):
    status: str
    user: BaseUser
