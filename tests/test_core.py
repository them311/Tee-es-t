from __future__ import annotations

import pytest

from snb.core.exceptions import RateLimitError, TransientError
from snb.core.retry import retry_async


@pytest.mark.asyncio
async def test_retry_succeeds_after_transient() -> None:
    attempts = {"n": 0}

    async def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise TransientError("try again")
        return "ok"

    result = await retry_async(flaky, max_attempts=5, base_delay=0.0)
    assert result == "ok"
    assert attempts["n"] == 3


@pytest.mark.asyncio
async def test_retry_gives_up() -> None:
    async def always_fails() -> None:
        raise TransientError("boom")

    with pytest.raises(TransientError):
        await retry_async(always_fails, max_attempts=2, base_delay=0.0)


@pytest.mark.asyncio
async def test_retry_honours_retry_after() -> None:
    state = {"n": 0}

    async def rate_limited() -> str:
        state["n"] += 1
        if state["n"] == 1:
            raise RateLimitError(retry_after=0.0)
        return "ok"

    assert await retry_async(rate_limited, max_attempts=3, base_delay=0.0) == "ok"
