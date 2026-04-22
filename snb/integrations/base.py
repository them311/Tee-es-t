"""Base class for integrations. Keeps every connector consistent:
- owns an AsyncHTTPClient configured with base_url + auth headers
- exposes ``aclose()`` and async context manager
- ``name`` used for logging + registry keys
"""

from __future__ import annotations

from abc import ABC
from typing import Any

from snb.config import get_logger
from snb.core.http import AsyncHTTPClient


class BaseIntegration(ABC):
    name: str = "base"

    def __init__(self, *, base_url: str, headers: dict[str, str] | None = None) -> None:
        self.log = get_logger(f"integration.{self.name}")
        self.http = AsyncHTTPClient(base_url=base_url, headers=headers or {})

    async def __aenter__(self) -> BaseIntegration:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self.http.aclose()
