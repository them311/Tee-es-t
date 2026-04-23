from __future__ import annotations

import pytest

from snb.agents.base import AgentContext, AgentResult
from snb.agents.registry import AgentRegistry


class _FakeAgent:
    name = "fake"
    interval_seconds = None

    def __init__(self) -> None:
        self.calls = 0

    async def run(self, ctx: AgentContext) -> AgentResult:
        self.calls += 1
        return AgentResult(ok=True, data=ctx.params)

    async def health(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_registry_run_one() -> None:
    reg = AgentRegistry()
    reg.register(_FakeAgent())  # type: ignore[arg-type]
    result = await reg.run_one("fake", x=1)
    assert result.ok
    assert result.data == {"x": "1"} or result.data == {"x": 1}


@pytest.mark.asyncio
async def test_registry_rejects_duplicates() -> None:
    reg = AgentRegistry()
    reg.register(_FakeAgent())  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        reg.register(_FakeAgent())  # type: ignore[arg-type]


def test_bootstrap_registers_built_in_agents() -> None:
    # bootstrap has module-level side effects — import it fresh.
    import importlib

    import snb.agents.registry as registry_mod

    # Reset the singleton to a fresh registry so prior tests don't pollute.
    registry_mod.registry = registry_mod.AgentRegistry()

    import snb.bootstrap  # noqa: F401

    importlib.reload(snb.bootstrap)

    names = {a.name for a in registry_mod.registry.all()}
    assert {"shopify_sync", "lead_enrichment", "outreach", "daily_digest"} <= names
