"""Indeed scraper — NOT YET IMPLEMENTED.

Indeed requires either their paid Publisher API or HTML scraping with
anti-bot handling. Leave this as a clean stub so the pipeline stays green
and a future session can plug in the real implementation.
"""

from __future__ import annotations

import logging

from ..models import Offer, Source
from .base import BaseScraper

log = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    source = Source.INDEED

    async def fetch(self) -> list[Offer]:
        log.info("IndeedScraper: not implemented, returning empty batch")
        return []
