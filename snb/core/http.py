"""Async HTTP client used by every integration/scraper.

Responsibilities:
- uniform timeout/retry behavior
- map transport failures to our exception hierarchy
- log request/response at DEBUG
- inject auth headers via a pluggable hook

Stays thin on top of httpx — if you need something exotic, reach for httpx
directly, don't stretch this wrapper.
"""

from __future__ import annotations

from typing import Any

import httpx

from snb.config import get_logger, get_settings
from snb.core.exceptions import (
    AuthError,
    IntegrationError,
    NotFoundError,
    RateLimitError,
    TransientError,
)
from snb.core.retry import retry_async

_log = get_logger("http")


class AsyncHTTPClient:
    def __init__(
        self,
        base_url: str = "",
        *,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = base_url
        self.default_headers = headers or {}
        self.timeout = timeout if timeout is not None else settings.http_timeout_seconds
        self.max_retries = max_retries if max_retries is not None else settings.http_max_retries
        self._external_client = client is not None
        self._client = client or httpx.AsyncClient(
            base_url=base_url,
            timeout=self.timeout,
            headers=self.default_headers,
        )

    async def __aenter__(self) -> AsyncHTTPClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        data: Any = None,
        headers: dict[str, str] | None = None,
        expect_json: bool = True,
    ) -> Any:
        async def _do() -> Any:
            _log.debug("{method} {url}", method=method, url=url)
            try:
                resp = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json,
                    data=data,
                    headers=headers,
                )
            except (httpx.TimeoutException, httpx.TransportError) as e:
                raise TransientError(str(e)) from e

            if resp.status_code == 429:
                retry_after = resp.headers.get("Retry-After")
                raise RateLimitError(retry_after=float(retry_after) if retry_after else None)
            if resp.status_code in (401, 403):
                raise AuthError(f"{resp.status_code} {resp.text[:200]}")
            if resp.status_code == 404:
                raise NotFoundError(f"{method} {url} -> 404")
            if resp.status_code >= 500:
                raise TransientError(f"{resp.status_code} {resp.text[:200]}")
            if resp.status_code >= 400:
                raise IntegrationError(f"{resp.status_code} {resp.text[:200]}")

            if not expect_json or not resp.content:
                return resp
            try:
                return resp.json()
            except ValueError as e:
                raise IntegrationError(f"invalid json: {e}") from e

        return await retry_async(_do, max_attempts=self.max_retries + 1)

    async def get(self, url: str, **kw: Any) -> Any:
        return await self.request("GET", url, **kw)

    async def post(self, url: str, **kw: Any) -> Any:
        return await self.request("POST", url, **kw)

    async def put(self, url: str, **kw: Any) -> Any:
        return await self.request("PUT", url, **kw)

    async def patch(self, url: str, **kw: Any) -> Any:
        return await self.request("PATCH", url, **kw)

    async def delete(self, url: str, **kw: Any) -> Any:
        return await self.request("DELETE", url, **kw)
