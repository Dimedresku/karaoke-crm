import os

from fastapi import UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, insert
import aiofiles
from typing import Any

from app.settings import settings
from app.models import User
from app.utils import verify_password, get_hashed_password
from app.schemas.user import CreateUser

def get_db():
    from app.main import database
    return database


async def get_auth_user_or_404(form_data: OAuth2PasswordRequestForm = Depends()) -> User:
    database = get_db()
    query = select(User).where(User.username == form_data.username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    hashed_pass = user.password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    return user


async def create_admin(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == "Guest" and form_data.password == "1234":
        payload = CreateUser(name="admin", username="admin", password=get_hashed_password("admin"))
        query = insert(User).values(**payload.dict())
        database = get_db()
        await database.execute(query)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def upload_file_with_directory(directory_name: str) -> Any:
    async def _upload_file(file: UploadFile = File(...)) -> str:
        destination = os.path.join(destination_dir, file.filename)
        async with aiofiles.open(destination, "wb") as out_file:
            while content := await file.read(1024):
                await out_file.write(content)

        return file.filename

    destination_dir = os.path.join(settings.STATIC_FILES_DIR, directory_name)
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    return _upload_file
