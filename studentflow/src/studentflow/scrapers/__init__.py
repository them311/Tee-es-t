"""Scrapers package.

Every scraper implements `BaseScraper` and appears in `SCRAPERS` so the
`ScraperAgent` can iterate on them without knowing the concrete types.
"""

from __future__ import annotations

from .base import BaseScraper
from .france_travail import FranceTravailScraper
from .hellowork import HelloWorkScraper
from .indeed import IndeedScraper
from .jobteaser import JobTeaserScraper
from .studentjob import StudentJobScraper

SCRAPERS: list[type[BaseScraper]] = [
    FranceTravailScraper,
    IndeedScraper,
    HelloWorkScraper,
    StudentJobScraper,
    JobTeaserScraper,
]

__all__ = [
    "SCRAPERS",
    "BaseScraper",
    "FranceTravailScraper",
    "HelloWorkScraper",
    "IndeedScraper",
    "JobTeaserScraper",
    "StudentJobScraper",
]
