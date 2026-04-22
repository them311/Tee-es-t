from __future__ import annotations

import pytest

from snb.pipelines.base import Pipeline, PipelineContext


@pytest.mark.asyncio
async def test_pipeline_runs_steps_in_order() -> None:
    async def double(_: PipelineContext, x: int) -> int:
        return x * 2

    async def plus_one(_: PipelineContext, x: int) -> int:
        return x + 1

    pipeline = Pipeline("t", steps=[double, plus_one])
    out = sorted(await pipeline.run([1, 2, 3]))
    assert out == [3, 5, 7]


@pytest.mark.asyncio
async def test_pipeline_filter_with_none() -> None:
    async def keep_even(_: PipelineContext, x: int) -> int | None:
        return x if x % 2 == 0 else None

    pipeline = Pipeline("t", steps=[keep_even])
    out = sorted(await pipeline.run([1, 2, 3, 4]))
    assert out == [2, 4]
