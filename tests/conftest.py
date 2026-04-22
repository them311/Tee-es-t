from __future__ import annotations

import os

import pytest

from snb.config import configure_logging


@pytest.fixture(autouse=True, scope="session")
def _quiet_logs() -> None:
    configure_logging(level="WARNING", json_mode=False)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensure tests never accidentally hit real credentials.
    for key in list(os.environ):
        if key.startswith(("AIRTABLE_", "HUBSPOT_", "SHOPIFY_", "GMAIL_", "NOTION_")):
            monkeypatch.delenv(key, raising=False)
