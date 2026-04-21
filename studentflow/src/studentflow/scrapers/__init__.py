"""Scrapers package (FRANCE ONLY).

Every scraper implements `BaseScraper` and appears in `SCRAPERS` so the
`ScraperAgent` can iterate on them without knowing the concrete types.

Only production-ready scrapers are registered. Stub/unimplemented scrapers
(StudentJob, JobTeaser) are excluded from the registry.
"""

from __future__ import annotations

from .adzuna import AdzunaScraper
from .base import BaseScraper
from .france_travail import FranceTravailScraper
from .hellowork import HelloWorkScraper
from .indeed import IndeedScraper
from .jooble import JoobleScraper

SCRAPERS: list[type[BaseScraper]] = [
    FranceTravailScraper,
    AdzunaScraper,
    JoobleScraper,
    HelloWorkScraper,
    IndeedScraper,
]

__all__ = [
    "SCRAPERS",
    "AdzunaScraper",
    "BaseScraper",
    "FranceTravailScraper",
    "HelloWorkScraper",
    "IndeedScraper",
    "JoobleScraper",
]
