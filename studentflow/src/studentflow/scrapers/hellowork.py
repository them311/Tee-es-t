"""HelloWork scraper — NOT YET IMPLEMENTED.

HelloWork exposes a public RSS feed per search. A minimal implementation
could parse `https://www.hellowork.com/fr-fr/emploi/recherche.html?k=<kw>&rss=1`.
Wiring plan:
  1. Fetch RSS via httpx.
  2. Parse with `defusedxml.ElementTree`.
  3. Map each item to `Offer`.
"""

from __future__ import annotations

import logging

from ..models import Offer, Source
from .base import BaseScraper

log = logging.getLogger(__name__)


class HelloWorkScraper(BaseScraper):
    source = Source.HELLOWORK

    async def fetch(self) -> list[Offer]:
        log.info("HelloWorkScraper: not implemented, returning empty batch")
        return []
