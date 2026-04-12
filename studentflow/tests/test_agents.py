"""Tests for agents using the in-memory repository."""

from __future__ import annotations

import pytest

from studentflow.agents import MatcherAgent, NotifierAgent, ScraperAgent
from studentflow.db import InMemoryRepository
from studentflow.models import Source
from studentflow.scrapers.base import BaseScraper

from .fixtures import make_offer, make_student


class _FakeScraper(BaseScraper):
    source = Source.INDEED

    def __init__(self, offers: list) -> None:  # type: ignore[no-untyped-def]
        self._offers = offers

    async def fetch(self):  # type: ignore[no-untyped-def]
        return self._offers


class _FailingScraper(BaseScraper):
    source = Source.HELLOWORK

    async def fetch(self):  # type: ignore[no-untyped-def]
        raise RuntimeError("boom")


@pytest.mark.asyncio
async def test_scraper_agent_upserts_and_isolates_errors() -> None:
    repo = InMemoryRepository()
    scrapers = [_FakeScraper([make_offer()]), _FailingScraper()]
    agent = ScraperAgent(repo, scrapers=scrapers)
    count = await agent.tick()
    assert count == 1
    assert len(repo.offers) == 1


@pytest.mark.asyncio
async def test_matcher_agent_creates_matches() -> None:
    repo = InMemoryRepository()
    repo.upsert_offers([make_offer()])
    student = make_student()
    repo.insert_student(student)

    agent = MatcherAgent(repo, threshold=0.6)
    created = await agent.tick()
    assert created == 1
    assert len(repo.matches) == 1


@pytest.mark.asyncio
async def test_notifier_agent_marks_notified_without_webhook() -> None:
    repo = InMemoryRepository()
    repo.upsert_offers([make_offer()])
    repo.insert_student(make_student())
    await MatcherAgent(repo, threshold=0.6).tick()

    notifier = NotifierAgent(repo, webhook_url="")
    sent = await notifier.tick()
    assert sent == 1
    assert all(m.notified_at is not None for m in repo.matches.values())
