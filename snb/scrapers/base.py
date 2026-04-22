"""Scraper base. Separates concerns strictly:

1. ``fetch(url)`` — transport (HTTP), cached retries, rate limiting
2. ``parse(raw)`` — extraction to structured Python
3. ``normalize(items)`` — clean, deduplicate, coerce types

Subclasses override ``parse`` (and optionally ``normalize``); ``run`` ties it
all together. This keeps parsers replaceable and testable in isolation.
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from snb.config import get_logger
from snb.core.http import AsyncHTTPClient


@dataclass
class ScrapeResult:
    items: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    source: str | None = None


class Scraper(ABC):
    name: str = "scraper"
    user_agent: str = "SNB-Scraper/1.0 (+https://snb-consulting.local)"
    rate_limit_seconds: float = 0.0  # min delay between requests

    def __init__(self) -> None:
        self.log = get_logger(f"scraper.{self.name}")
        self.http = AsyncHTTPClient(headers={"User-Agent": self.user_agent})
        self._last_request_ts: float = 0.0

    async def aclose(self) -> None:
        await self.http.aclose()

    async def fetch(self, url: str, **kw: Any) -> Any:
        if self.rate_limit_seconds:
            loop = asyncio.get_event_loop()
            now = loop.time()
            elapsed = now - self._last_request_ts
            if elapsed < self.rate_limit_seconds:
                await asyncio.sleep(self.rate_limit_seconds - elapsed)
            self._last_request_ts = loop.time()
        return await self.http.get(url, expect_json=False, **kw)

    @abstractmethod
    async def parse(self, raw: Any) -> list[dict[str, Any]]: ...

    async def normalize(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return items

    async def run(self, *urls: str) -> ScrapeResult:
        result = ScrapeResult(source=self.name)
        for url in urls:
            try:
                raw = await self.fetch(url)
                parsed = await self.parse(raw)
                result.items.extend(await self.normalize(parsed))
            except Exception as e:  # noqa: BLE001
                self.log.exception("scrape failed for {url}: {err}", url=url, err=str(e))
                result.errors.append(f"{url}: {e}")
        return result
