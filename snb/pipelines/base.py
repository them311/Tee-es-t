"""Async pipeline primitives.

A Step is an async callable ``(ctx, item) -> item | None``. Returning None
filters the item out of downstream steps.

A Pipeline threads items through its Steps sequentially. Concurrency is handled
per pipeline via ``max_concurrency`` — we fan out the per-item chain, not the
steps, so ordering inside a step is preserved.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable, Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from snb.config import get_logger

Step = Callable[["PipelineContext", Any], Awaitable[Any]]


@dataclass
class PipelineContext:
    run_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    def __init__(self, name: str, steps: list[Step], *, max_concurrency: int = 8) -> None:
        self.name = name
        self.steps = steps
        self.max_concurrency = max_concurrency
        self.log = get_logger(f"pipeline.{name}")

    async def _run_one(self, ctx: PipelineContext, item: Any, sem: asyncio.Semaphore) -> Any:
        async with sem:
            current = item
            for step in self.steps:
                current = await step(ctx, current)
                if current is None:
                    return None
            return current

    async def run(
        self,
        items: AsyncIterable[Any] | list[Any],
        ctx: PipelineContext | None = None,
    ) -> list[Any]:
        ctx = ctx or PipelineContext()
        sem = asyncio.Semaphore(self.max_concurrency)
        tasks: list[asyncio.Task[Any]] = []

        if isinstance(items, list):
            for it in items:
                tasks.append(asyncio.create_task(self._run_one(ctx, it, sem)))
        else:
            async for it in items:
                tasks.append(asyncio.create_task(self._run_one(ctx, it, sem)))

        done = await asyncio.gather(*tasks, return_exceptions=True)
        out: list[Any] = []
        for r in done:
            if isinstance(r, Exception):
                self.log.exception("step error: {err}", err=str(r))
                continue
            if r is not None:
                out.append(r)
        return out
