"""In-memory pub/sub for the real-time match stream.

Lightweight broadcaster the MatcherAgent pushes to every time it creates a
match, and that the SSE endpoint fans out to connected student browsers.

Design is deliberately modest: one `asyncio.Queue` per subscriber, keyed by
`student_id`. Fine for a single API process (the default Netlify/Railway
deployment). If StudentFlow grows to multiple API workers, swap this module
for Redis pub/sub without touching any caller — the public surface is just
`publish` / `subscribe`.
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress
from uuid import UUID

log = logging.getLogger(__name__)


class MatchBroadcaster:
    """Fan-out queue keyed by student id.

    `publish()` is best-effort: it drops events rather than blocking if a
    subscriber's queue is saturated, so a slow browser can never stall the
    matcher.
    """

    def __init__(self, max_queue: int = 32) -> None:
        self._subs: dict[UUID, list[asyncio.Queue[dict]]] = defaultdict(list)
        self._max_queue = max_queue

    def publish(self, student_id: UUID, event: dict) -> int:
        """Push `event` to every subscriber of `student_id`. Returns count."""
        queues = list(self._subs.get(student_id, ()))
        delivered = 0
        for q in queues:
            try:
                q.put_nowait(event)
                delivered += 1
            except asyncio.QueueFull:
                log.warning("Dropping SSE event for student %s (queue full)", student_id)
        return delivered

    @asynccontextmanager
    async def subscribe(self, student_id: UUID) -> AsyncIterator[asyncio.Queue[dict]]:
        """Async context manager yielding an event queue for this student."""
        queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=self._max_queue)
        self._subs[student_id].append(queue)
        try:
            yield queue
        finally:
            with suppress(ValueError):
                self._subs[student_id].remove(queue)
            if not self._subs[student_id]:
                self._subs.pop(student_id, None)


# Module-level singleton. The API and the MatcherAgent both import this one.
broadcaster = MatchBroadcaster()
