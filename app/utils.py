import os

from passlib.context import CryptContext

from app.settings import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def delete_avatar(url: str):
    file_name = os.path.basename(url)
    path = f'{settings.STATIC_FILES_DIR}/users/{file_name}'
    if file_name and os.path.exists(path):
        os.remove(path)
