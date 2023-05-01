from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    status: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class SystemUser(BaseModel):
    username: str
    id: int
    avatar: str

    class Config:
        orm_mode = True


class UserResponse:
    id: int
