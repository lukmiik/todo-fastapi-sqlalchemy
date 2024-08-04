from functools import cache

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    """Settings class for the project."""

    model_config = pydantic_settings.SettingsConfigDict(extra="ignore")

    FERNET_KEY: str = "oikBWDid816xrCYZMj_w20YTv1sN4_WhwZK9Kdd9AIs="
    DB_URL: str = "sqlite:///./todo.db"

    @classmethod
    @cache
    def get_settings(cls) -> "Settings":
        """Returns settings class instance."""
        return Settings()
