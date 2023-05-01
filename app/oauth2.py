import base64
from typing import Union, Any
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select

from app.models import User
from app.settings import settings
from app.dependencies import get_db

JWT_PUBLIC_KEY: str = base64.b64decode(settings.JWT_PUBLIC_KEY).decode('utf-8')
JWT_PRIVATE_KEY: str = base64.b64decode(settings.JWT_PRIVATE_KEY).decode('utf-8')


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES_IN)

    to_encode = {"exp": expires_delta, "iat": datetime.utcnow(), "subject": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.now() + expires_delta
    else:
        expires_delta = datetime.now() + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES_IN)

    to_encode = {"exp": expires_delta, "iat": datetime.utcnow(),"subject": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, JWT_PRIVATE_KEY, settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token):
    try:
        payload = jwt.decode(token, JWT_PUBLIC_KEY, settings.JWT_ALGORITHM)
        if payload['type'] == 'access':
            return payload['subject']
        raise HTTPException(status_code=401, detail='Scope for the token is invalid')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid token')


def refresh_auth_token(refresh_token):
    try:
        payload = jwt.decode(refresh_token, JWT_PUBLIC_KEY, settings.JWT_ALGORITHM)
        if payload['type'] == 'refresh':
            user_id = payload['subject']
            new_token = create_access_token(user_id)
            return new_token
        raise HTTPException(status_code=401, detail='Invalid scope for token')
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Refresh token expired')
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail='Invalid refresh token')


async def get_auth_user_by_token(credentials: HTTPAuthorizationCredentials = Security(HTTPBearer())):
    user_id = decode_token(credentials.credentials)
    database = get_db()
    query = select(User.id, User.username, User.avatar).where(User.id == int(user_id))
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return user
