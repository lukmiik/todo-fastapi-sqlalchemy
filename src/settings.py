from functools import cache

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """Settings class for the project."""

    model_config = pydantic_settings.SettingsConfigDict(extra="ignore")

    FERNET_KEY: str = "oikBWDid816xrCYZMj_w20YTv1sN4_WhwZK9Kdd9AIs="
    DB_URL: str = "sqlite:///./todo.db"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    REFRESH_SECRET_KEY: str = (
        "5b4bb4e6fe7862a28986e6dfdfd7b7087f0a61385f28e32ce9284295a3ce2781afc97-refresh"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 180
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1800
    ALGORITHM: str = "HS256"

    @classmethod
    @cache
    def get_settings(cls) -> "Settings":
        """Returns settings class instance."""
        return Settings()
