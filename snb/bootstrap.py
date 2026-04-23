"""Bootstrap: register every built-in agent once at import time.

Importing this module has side-effects — it mutates the global ``registry``.
Do it exactly once at the process entry (CLI, API, worker).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from snb.agents.base import Agent, AgentContext, AgentResult
from snb.agents.digest import DailyDigestAgent
from snb.agents.lead_enrichment import LeadEnrichmentAgent
from snb.agents.outreach import OutreachAgent
from snb.agents.registry import registry
from snb.agents.shopify_sync import ShopifySyncAgent
from snb.config import get_logger

_log = get_logger("bootstrap")
_LOG_FILE = Path("data/job_log.jsonl")


class _LoggingAgent(Agent):
    """Transparent wrapper that records every run to ``data/job_log.jsonl``.

    Keeps the digest agent source-of-truth without forcing every concrete agent
    to care about persistence.
    """

    def __init__(self, inner: Agent) -> None:
        super().__init__()
        self._inner = inner
        self.name = inner.name
        self.interval_seconds = inner.interval_seconds

    async def run(self, ctx: AgentContext) -> AgentResult:
        started = datetime.now(timezone.utc)
        try:
            result = await self._inner.run(ctx)
        except Exception as e:  # noqa: BLE001
            result = AgentResult(ok=False, error=str(e))
        _write_event(
            {
                "ts": started.isoformat(),
                "agent": self.name,
                "ok": result.ok,
                "error": result.error,
                "metrics": result.metrics,
            }
        )
        return result


def _write_event(event: dict) -> None:
    try:
        _LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, default=str) + "\n")
    except OSError as e:  # pragma: no cover
        _log.warning("job log write failed: {err}", err=str(e))


def _register_once() -> None:
    if registry.all():
        return
    for agent_cls in (
        ShopifySyncAgent,
        LeadEnrichmentAgent,
        OutreachAgent,
        DailyDigestAgent,
    ):
        registry.register(_LoggingAgent(agent_cls()))
    _log.info("registered {n} agents", n=len(registry.all()))


_register_once()
