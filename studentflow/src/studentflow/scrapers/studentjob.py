"""StudentJob scraper — NOT IMPLEMENTED / NOT READY.

Target: https://www.studentjob.fr/ — no public API, HTML scraping required.

STATUS: This scraper is a placeholder. It is NOT registered in the SCRAPERS
registry and will NOT be called by the ScraperAgent. Do not import or use
this module in production until a real implementation is provided.
"""

from __future__ import annotations

import logging

from ..models import Offer, Source
from .base import BaseScraper

log = logging.getLogger(__name__)


class StudentJobScraper(BaseScraper):
    """Placeholder — not implemented. Not registered in SCRAPERS."""

    source = Source.STUDENTJOB

    async def fetch(self) -> list[Offer]:
        log.warning("StudentJobScraper: NOT IMPLEMENTED — returning empty batch")
        return []
