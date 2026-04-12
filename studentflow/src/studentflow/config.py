"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # France Travail
    france_travail_client_id: str = ""
    france_travail_client_secret: str = ""

    # Agents
    scraper_interval_seconds: int = Field(default=900, ge=10)
    matcher_interval_seconds: int = Field(default=60, ge=5)
    notifier_interval_seconds: int = Field(default=30, ge=5)
    match_score_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Notifications
    notification_webhook_url: str = ""

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_key)

    @property
    def france_travail_configured(self) -> bool:
        return bool(self.france_travail_client_id and self.france_travail_client_secret)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
