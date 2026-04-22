"""Async helpers used across the package."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Iterable
from typing import TypeVar

T = TypeVar("T")


async def gather_limited(aws: Iterable[Awaitable[T]], *, limit: int = 16) -> list[T]:
    """``asyncio.gather`` with a concurrency cap."""
    sem = asyncio.Semaphore(limit)

    async def _wrap(aw: Awaitable[T]) -> T:
        async with sem:
            return await aw

    return await asyncio.gather(*(_wrap(a) for a in aws))


def run_sync(coro: Awaitable[T]) -> T:
    """Run an async coroutine synchronously. Useful for CLI/script entrypoints."""
    return asyncio.run(coro)  # type: ignore[arg-type]
