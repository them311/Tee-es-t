"""Agent primitives.

An Agent is a self-contained async unit with:
- a name (used by the registry + CLI)
- a ``run(ctx)`` coroutine producing an AgentResult
- optional periodic scheduling (``interval_seconds``) for orchestrator loops

Keep agents small and composable — chain them via pipelines or a scheduler.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from snb.config import get_logger


@dataclass
class AgentContext:
    params: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    ok: bool = True
    data: Any = None
    error: str | None = None
    metrics: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    name: str = "agent"
    interval_seconds: float | None = None

    def __init__(self) -> None:
        self.log = get_logger(f"agent.{self.name}")

    @abstractmethod
    async def run(self, ctx: AgentContext) -> AgentResult: ...

    async def health(self) -> bool:
        return True
