from fastapi import APIRouter, Depends, Security, Response, status, Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import TokenSchema, SystemUser
from app.dependencies import get_auth_user_or_404
from app.models import User
from app.settings import settings
from app.oauth2 import (
    create_access_token,
    create_refresh_token,
    get_auth_user_by_token,
    refresh_auth_token,
)

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
security = HTTPBearer()


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenSchema)
async def login(response: Response, user: User = Depends(get_auth_user_or_404)):
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(key="access_token",
                        value=access_token,
                        max_age=ACCESS_TOKEN_EXPIRES_IN,
                        path="/",
                        domain=None,
                        secure=True,
                        httponly=True,
                        samesite='none')
    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        max_age=REFRESH_TOKEN_EXPIRES_IN,
                        path="/",
                        domain=None,
                        secure=True,
                        httponly=True,
                        samesite='none')

    return {'status': 'success', 'access_token': access_token, 'refresh_token': refresh_token}


@router.get("/logout")
async def logout(response: Response, request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    credentials = HTTPAuthorizationCredentials(credentials=token, scheme='')
    await get_auth_user_by_token(credentials)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    response.status_code = status.HTTP_200_OK
    return response


@router.post("/refresh", response_model=TokenSchema)
async def refresh_token(response: Response, credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    new_access_token = refresh_auth_token(token)
    response.set_cookie(key="access_token",
                        value=new_access_token,
                        max_age=ACCESS_TOKEN_EXPIRES_IN,
                        path="/",
                        domain=None,
                        secure=True,
                        httponly=True,
                        samesite='none')

    return {'status': 'success', 'access_token': new_access_token, 'refresh_token': token}


@router.get("/get-user", response_model=SystemUser)
async def get_user(user: User = Depends(get_auth_user_by_token)):
    return SystemUser.from_orm(user).dict()
