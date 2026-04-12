"""Autonomous agent loops.

Three agents that the orchestrator launches concurrently. Each one is a
stateless loop that reads/writes through the Repository — no in-process state
so you can kill and restart them safely.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

import httpx

from .config import Settings, get_settings
from .db import Repository
from .matching import rank_students_for_offer
from .models import Match, Offer
from .scrapers import SCRAPERS, BaseScraper

log = logging.getLogger(__name__)


class ScraperAgent:
    """Calls every registered scraper in parallel and upserts offers."""

    def __init__(self, repo: Repository, scrapers: list[BaseScraper] | None = None) -> None:
        self.repo = repo
        self.scrapers = scrapers or [cls() for cls in SCRAPERS]  # type: ignore[call-arg]

    async def tick(self) -> int:
        results = await asyncio.gather(
            *(self._run_one(s) for s in self.scrapers), return_exceptions=True
        )
        all_offers: list[Offer] = []
        for scraper, result in zip(self.scrapers, results, strict=True):
            if isinstance(result, BaseException):
                log.exception("Scraper %s failed", scraper.source.value, exc_info=result)
                continue
            all_offers.extend(result)
        return self.repo.upsert_offers(all_offers)

    async def _run_one(self, scraper: BaseScraper) -> list[Offer]:
        log.info("Running scraper %s", scraper.source.value)
        offers = await scraper.fetch()
        log.info("Scraper %s returned %d offers", scraper.source.value, len(offers))
        return offers


class MatcherAgent:
    """Scores recent offers against active students and writes matches."""

    def __init__(self, repo: Repository, threshold: float) -> None:
        self.repo = repo
        self.threshold = threshold

    async def tick(self) -> int:
        offers = self.repo.list_recent_unmatched_offers()
        students = self.repo.list_active_students()
        if not offers or not students:
            return 0

        created = 0
        for offer in offers:
            ranked = rank_students_for_offer(offer, students, threshold=self.threshold)
            for student, result in ranked:
                match = Match(
                    offer_id=offer.id,
                    student_id=student.id,
                    score=result.score,
                    reasons=result.reasons,
                )
                self.repo.insert_match(match)
                created += 1
        log.info("MatcherAgent: %d matches created", created)
        return created


class NotifierAgent:
    """Sends notifications for unnotified matches via a webhook."""

    def __init__(self, repo: Repository, webhook_url: str) -> None:
        self.repo = repo
        self.webhook_url = webhook_url

    async def tick(self) -> int:
        pending = self.repo.list_unnotified_matches()
        if not pending:
            return 0
        if not self.webhook_url:
            log.warning("NotifierAgent: no webhook configured, marking %d as notified",
                        len(pending))
            for m in pending:
                self.repo.mark_match_notified(m.id)
            return len(pending)

        sent = 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            for match in pending:
                try:
                    resp = await client.post(
                        self.webhook_url,
                        json={
                            "match_id": str(match.id),
                            "offer_id": str(match.offer_id),
                            "student_id": str(match.student_id),
                            "score": match.score,
                            "reasons": match.reasons,
                            "sent_at": datetime.utcnow().isoformat(),
                        },
                    )
                    resp.raise_for_status()
                    self.repo.mark_match_notified(match.id)
                    sent += 1
                except httpx.HTTPError as exc:
                    log.warning("Notification failed for match %s: %s", match.id, exc)
        return sent


async def run_forever(repo: Repository, settings: Settings | None = None) -> None:
    """Launch the three agents concurrently and keep them running."""
    settings = settings or get_settings()

    scraper_agent = ScraperAgent(repo)
    matcher_agent = MatcherAgent(repo, threshold=settings.match_score_threshold)
    notifier_agent = NotifierAgent(repo, webhook_url=settings.notification_webhook_url)

    await asyncio.gather(
        _loop("scraper", scraper_agent.tick, settings.scraper_interval_seconds),
        _loop("matcher", matcher_agent.tick, settings.matcher_interval_seconds),
        _loop("notifier", notifier_agent.tick, settings.notifier_interval_seconds),
    )


async def _loop(name: str, tick_fn, interval: int) -> None:  # type: ignore[no-untyped-def]
    log.info("Starting %s loop (every %ds)", name, interval)
    while True:
        try:
            processed = await tick_fn()
            log.info("%s tick: %s items", name, processed)
        except Exception:
            log.exception("%s tick failed", name)
        await asyncio.sleep(interval)
