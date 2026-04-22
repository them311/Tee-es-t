from __future__ import annotations

from snb.config import Settings, get_settings
from snb.config.settings import AirtableSettings


def test_defaults_load_without_env() -> None:
    s = Settings()
    assert s.app_name == "snb"
    assert s.env in ("dev", "staging", "prod")
    assert s.http_max_retries >= 0


def test_get_settings_is_cached() -> None:
    assert get_settings() is get_settings()


def test_nested_integration_settings_default_empty() -> None:
    at = AirtableSettings()
    assert at.api_key is None
    assert at.base_id is None
