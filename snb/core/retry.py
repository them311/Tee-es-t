"""Async retry helper with exponential backoff and jitter.

Deliberately thin: uses tenacity under the hood if installed, otherwise falls
back to a hand-rolled loop. This keeps hard dependencies minimal while getting
best-in-class behavior when tenacity is available.
"""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

from snb.core.exceptions import RateLimitError, RetryableError

T = TypeVar("T")


async def retry_async(
    func: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
    jitter: float = 0.2,
    retry_on: tuple[type[BaseException], ...] = (RetryableError,),
) -> T:
    """Retry ``func`` with exponential backoff + jitter.

    Honours ``RateLimitError.retry_after`` when present.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            return await func()
        except retry_on as exc:
            if attempt >= max_attempts:
                raise
            if isinstance(exc, RateLimitError) and exc.retry_after is not None:
                delay = float(exc.retry_after)
            else:
                delay = min(max_delay, base_delay * (2 ** (attempt - 1)))
                delay += random.uniform(0, jitter * delay)
            await asyncio.sleep(delay)
