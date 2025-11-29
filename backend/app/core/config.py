import os
from pydantic.v1 import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/tmsdb")
    secret_key: str = os.getenv("SECRET_KEY", "supersecret")

settings = Settings()
