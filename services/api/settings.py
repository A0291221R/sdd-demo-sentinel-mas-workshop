from pydantic_settings import BaseSettings

__all__ = ["Settings", "settings"]


class Settings(BaseSettings):
    queue_url: str


settings: Settings = Settings()
