import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URI: str = "postgresql://postgres:postgres@db:5432/postgres"
    STATIC_FILES_DIR: str = os.path.join(os.path.dirname(__file__), "static")
    ACCESS_TOKEN_EXPIRES_IN: int = 60 * 60  # 60 minutes
    REFRESH_TOKEN_EXPIRES_IN: int = 60 * 60 * 24 * 7  # 7 days
    JWT_ALGORITHM: str = "RS256"
    JWT_PUBLIC_KEY: str
    JWT_PRIVATE_KEY: str

settings = Settings()
