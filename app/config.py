from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    # Existing Config
    DATABASE_URL: str = Field(...)
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)

    # New Email Config
    MAIL_USERNAME: str = Field(...)
    MAIL_PASSWORD: str = Field(...)
    MAIL_FROM: str = Field(...)
    MAIL_PORT: int = Field(default=587)
    MAIL_SERVER: str = Field(...)
    MAIL_FROM_NAME: str = Field(default="My App Team")
    MAIL_STARTTLS: bool = Field(default=True)
    MAIL_SSL_TLS: bool = Field(default=False)
    USE_CREDENTIALS: bool = Field(default=True)

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

# Backwards compatible exports
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS
DATABASE_URL = settings.DATABASE_URL