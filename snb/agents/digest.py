"""Daily operational digest.

Reads job-log entries for the last 24h and emails a short summary. If Claude
is available, it rewrites the raw counts into a human digest. Otherwise it
falls back to a plain-text table.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from snb.agents.base import Agent, AgentContext, AgentResult
from snb.config import get_settings

_LOG_FILE = Path("data/job_log.jsonl")

DIGEST_SYSTEM = """You are an ops manager. Summarise yesterday's automation activity in 6-8 bullet lines in French.
- Mention the top 2 wins, the top 2 risks, and 1 recommended action.
- Be concrete (numbers, agent names). No filler, no apologies."""


class DailyDigestAgent(Agent):
    name = "daily_digest"
    interval_seconds: float = 86400.0  # 24h

    async def run(self, ctx: AgentContext) -> AgentResult:
        recipient = ctx.params.get("to") or get_settings().gmail.sender
        if not recipient:
            return AgentResult(ok=False, error="no recipient (GMAIL_SENDER or param 'to')")

        events = _read_recent_events(timedelta(hours=24))
        summary_raw = _render_plain(events)

        try:
            from snb.llm import AnthropicClient, ChatMessage

            llm = AnthropicClient()
            summary = await llm.chat(
                [ChatMessage(role="user", content=summary_raw)],
                system=DIGEST_SYSTEM,
            )
        except Exception as e:  # noqa: BLE001
            self.log.info("LLM unavailable, sending raw digest: {err}", err=str(e))
            summary = summary_raw

        try:
            from snb.integrations.gmail import GmailClient

            gmail = GmailClient()
            try:
                await gmail.send(
                    to=recipient,
                    subject=f"SNB — Daily digest {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
                    body=summary,
                )
            finally:
                await gmail.aclose()
        except Exception as e:  # noqa: BLE001
            return AgentResult(ok=False, error=f"send failed: {e}")

        return AgentResult(ok=True, data={"events": len(events)})


def _read_recent_events(window: timedelta) -> list[dict]:
    if not _LOG_FILE.exists():
        return []
    cutoff = datetime.now(timezone.utc) - window
    events: list[dict] = []
    for line in _LOG_FILE.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        try:
            ts = datetime.fromisoformat(ev.get("ts", ""))
        except ValueError:
            continue
        if ts >= cutoff:
            events.append(ev)
    return events


def _render_plain(events: list[dict]) -> str:
    if not events:
        return "No automation activity in the last 24h."
    by_agent: dict[str, dict[str, int]] = {}
    for e in events:
        name = e.get("agent", "unknown")
        bucket = by_agent.setdefault(name, {"runs": 0, "ok": 0, "errors": 0})
        bucket["runs"] += 1
        if e.get("ok"):
            bucket["ok"] += 1
        else:
            bucket["errors"] += 1
    lines = [f"{len(events)} runs across {len(by_agent)} agents in the last 24h:"]
    for name, b in sorted(by_agent.items()):
        lines.append(f"  - {name}: {b['runs']} runs, {b['ok']} ok, {b['errors']} errors")
    return "\n".join(lines)
