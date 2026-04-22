"""In-process agent registry + lightweight scheduler.

The scheduler is intentionally naive (asyncio + sleep). For production-grade
periodic orchestration, plug in APScheduler/Celery Beat. For now, this is
enough to wire CLI commands and docker workers.
"""

from __future__ import annotations

import asyncio
from typing import Any

from snb.agents.base import Agent, AgentContext, AgentResult
from snb.config import get_logger

_log = get_logger("registry")


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> Agent:
        if agent.name in self._agents:
            raise ValueError(f"agent '{agent.name}' already registered")
        self._agents[agent.name] = agent
        return agent

    def get(self, name: str) -> Agent:
        if name not in self._agents:
            raise KeyError(f"unknown agent '{name}'")
        return self._agents[name]

    def all(self) -> list[Agent]:
        return list(self._agents.values())

    async def run_one(self, name: str, **params: Any) -> AgentResult:
        agent = self.get(name)
        return await agent.run(AgentContext(params=params))

    async def run_scheduled(self) -> None:
        """Spin a task per agent that has ``interval_seconds`` set."""
        tasks = [
            asyncio.create_task(self._loop(a))
            for a in self._agents.values()
            if a.interval_seconds
        ]
        if not tasks:
            _log.warning("no scheduled agents registered")
            return
        await asyncio.gather(*tasks)

    async def _loop(self, agent: Agent) -> None:
        assert agent.interval_seconds is not None
        while True:
            try:
                res = await agent.run(AgentContext())
                if not res.ok:
                    agent.log.warning("agent run failed: {err}", err=res.error)
            except Exception as e:  # noqa: BLE001
                agent.log.exception("agent crashed: {err}", err=str(e))
            await asyncio.sleep(agent.interval_seconds)


registry = AgentRegistry()
