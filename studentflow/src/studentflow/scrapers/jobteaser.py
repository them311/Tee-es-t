"""JobTeaser scraper — NOT IMPLEMENTED / NOT READY.

JobTeaser (Career Center partner for many schools) requires authenticated
access per school. Typical flow: OAuth via the school's portal.

STATUS: This scraper is a placeholder. It is NOT registered in the SCRAPERS
registry and will NOT be called by the ScraperAgent. Do not import or use
this module in production until a real implementation is provided.
"""

from __future__ import annotations

import logging

from ..models import Offer, Source
from .base import BaseScraper

log = logging.getLogger(__name__)


class JobTeaserScraper(BaseScraper):
    """Placeholder — not implemented. Not registered in SCRAPERS."""

    source = Source.JOBTEASER

    async def fetch(self) -> list[Offer]:
        log.warning("JobTeaserScraper: NOT IMPLEMENTED — returning empty batch")
        return []
