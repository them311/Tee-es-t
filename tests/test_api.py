from __future__ import annotations

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:  # api extra not installed
    TestClient = None  # type: ignore[assignment]


pytestmark = pytest.mark.skipif(TestClient is None, reason="api extra not installed")


def _client() -> "TestClient":
    from snb.api.app import create_app

    return TestClient(create_app())


def test_health_ok() -> None:
    with _client() as c:
        r = c.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["ok"] is True
        assert body["service"] == "snb"
        assert "agents" in body


def test_webhook_lead_requires_email() -> None:
    with _client() as c:
        r = c.post("/webhook/lead", json={"first_name": "ada"})
        assert r.status_code == 422
