"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache

import logging

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_log = logging.getLogger(__name__)


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

    # Adzuna (official public API, free tier) — FRANCE ONLY
    adzuna_app_id: str = ""
    adzuna_app_key: str = ""
    adzuna_country: str = "fr"

    @field_validator("adzuna_country")
    @classmethod
    def _force_adzuna_fr(cls, v: str) -> str:
        if v != "fr":
            _log.warning("ADZUNA_COUNTRY='%s' is not supported — forcing 'fr'", v)
            return "fr"
        return v

    # Jooble (official public API, single free key) — FRANCE ONLY
    jooble_api_key: str = ""
    jooble_location: str = "France"

    @field_validator("jooble_location")
    @classmethod
    def _force_jooble_france(cls, v: str) -> str:
        if v != "France":
            _log.warning("JOOBLE_LOCATION='%s' is not supported — forcing 'France'", v)
            return "France"
        return v

    # Agents
    scraper_interval_seconds: int = Field(default=900, ge=10)
    matcher_interval_seconds: int = Field(default=60, ge=5)
    notifier_interval_seconds: int = Field(default=30, ge=5)
    match_score_threshold: float = Field(default=0.6, ge=0.0, le=1.0)

    # Scoring weights (configurable via env vars, auto-normalized to sum to 1.0)
    weight_skills: float = Field(default=0.40, ge=0.0)
    weight_location: float = Field(default=0.25, ge=0.0)
    weight_contract: float = Field(default=0.15, ge=0.0)
    weight_hours: float = Field(default=0.10, ge=0.0)
    weight_availability: float = Field(default=0.10, ge=0.0)

    @model_validator(mode="after")
    def _normalize_weights(self) -> "Settings":
        """Auto-normalize scoring weights so they always sum to 1.0."""
        total = (
            self.weight_skills
            + self.weight_location
            + self.weight_contract
            + self.weight_hours
            + self.weight_availability
        )
        if total <= 0:
            # Fallback to equal weights if all are zero.
            self.weight_skills = 0.20
            self.weight_location = 0.20
            self.weight_contract = 0.20
            self.weight_hours = 0.20
            self.weight_availability = 0.20
        elif abs(total - 1.0) > 1e-9:
            self.weight_skills /= total
            self.weight_location /= total
            self.weight_contract /= total
            self.weight_hours /= total
            self.weight_availability /= total
        return self

    @property
    def scoring_weights(self) -> dict[str, float]:
        """Return the normalized scoring weights as a dict."""
        return {
            "skills": self.weight_skills,
            "location": self.weight_location,
            "contract": self.weight_contract,
            "hours": self.weight_hours,
            "availability": self.weight_availability,
        }

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    # Public base URL used to build accept/decline links embedded in emails.
    # In prod, set this to the API's public hostname (e.g. https://api.studentflow.fr).
    public_base_url: str = "http://localhost:8000"

    # Notifications — webhook (fallback / bridge to Make/Zapier/n8n)
    notification_webhook_url: str = ""

    # Notifications — SMTP email (preferred channel, direct to student)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True

    @property
    def supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_service_key)

    @property
    def france_travail_configured(self) -> bool:
        return bool(self.france_travail_client_id and self.france_travail_client_secret)

    @property
    def adzuna_configured(self) -> bool:
        return bool(self.adzuna_app_id and self.adzuna_app_key)

    @property
    def jooble_configured(self) -> bool:
        return bool(self.jooble_api_key)

    @property
    def smtp_configured(self) -> bool:
        return bool(self.smtp_host and self.smtp_from)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
