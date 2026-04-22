"""Typed environment settings loaded from .env / process env.

Central entrypoint: ``get_settings()`` returns a cached, validated Settings object.

Add integration-specific settings as nested models so each client can pull its
own slice without leaking unrelated config.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class _Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


class GmailSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="GMAIL_", env_file=ENV_FILE, extra="ignore")
    client_id: SecretStr | None = None
    client_secret: SecretStr | None = None
    refresh_token: SecretStr | None = None
    sender: str | None = None


class AirtableSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="AIRTABLE_", env_file=ENV_FILE, extra="ignore")
    api_key: SecretStr | None = None
    base_id: str | None = None


class HubSpotSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="HUBSPOT_", env_file=ENV_FILE, extra="ignore")
    access_token: SecretStr | None = None
    portal_id: str | None = None


class ShopifySettings(_Base):
    model_config = SettingsConfigDict(env_prefix="SHOPIFY_", env_file=ENV_FILE, extra="ignore")
    shop_domain: str | None = None
    access_token: SecretStr | None = None
    api_version: str = "2024-10"


class NotionSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="NOTION_", env_file=ENV_FILE, extra="ignore")
    token: SecretStr | None = None
    root_page_id: str | None = None


class GoogleSheetsSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="GSHEETS_", env_file=ENV_FILE, extra="ignore")
    service_account_json: str | None = None  # path or inline JSON


class DatabaseSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=ENV_FILE, extra="ignore")
    url: str = "sqlite+aiosqlite:///./snb.db"
    echo: bool = False
    pool_size: int = 5


class RedisSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="REDIS_", env_file=ENV_FILE, extra="ignore")
    url: str = "redis://localhost:6379/0"


class LLMSettings(_Base):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_file=ENV_FILE, extra="ignore")
    anthropic_api_key: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    default_model: str = "claude-sonnet-4-6"


class Settings(_Base):
    app_name: str = "snb"
    env: Literal["dev", "staging", "prod"] = Field(default="dev")
    debug: bool = True
    log_level: str = "INFO"
    log_json: bool = False

    http_timeout_seconds: float = 30.0
    http_max_retries: int = 3

    gmail: GmailSettings = Field(default_factory=GmailSettings)
    airtable: AirtableSettings = Field(default_factory=AirtableSettings)
    hubspot: HubSpotSettings = Field(default_factory=HubSpotSettings)
    shopify: ShopifySettings = Field(default_factory=ShopifySettings)
    notion: NotionSettings = Field(default_factory=NotionSettings)
    gsheets: GoogleSheetsSettings = Field(default_factory=GoogleSheetsSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    llm: LLMSettings = Field(default_factory=LLMSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
