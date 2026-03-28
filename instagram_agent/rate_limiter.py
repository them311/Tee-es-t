"""Rate limiter to stay within Instagram API and platform limits."""

import logging
import time
from collections import deque
from datetime import datetime, timedelta

from .config import RateLimitConfig

logger = logging.getLogger(__name__)


class RateLimiter:
    """Tracks and enforces rate limits for API actions."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._hourly_timestamps: deque[datetime] = deque()
        self._daily_timestamps: deque[datetime] = deque()

    @property
    def hourly_count(self) -> int:
        self._prune_old_entries()
        return len(self._hourly_timestamps)

    @property
    def daily_count(self) -> int:
        self._prune_old_entries()
        return len(self._daily_timestamps)

    def can_proceed(self) -> bool:
        self._prune_old_entries()
        if len(self._hourly_timestamps) >= self.config.max_comments_per_hour:
            logger.warning(f"Hourly limit reached ({self.config.max_comments_per_hour}/h)")
            return False
        if len(self._daily_timestamps) >= self.config.max_comments_per_day:
            logger.warning(f"Daily limit reached ({self.config.max_comments_per_day}/day)")
            return False
        return True

    def record_action(self):
        now = datetime.now()
        self._hourly_timestamps.append(now)
        self._daily_timestamps.append(now)

    def wait_if_needed(self):
        """Block until we can proceed, respecting the delay between comments."""
        while not self.can_proceed():
            logger.info("Rate limit reached, waiting 60s...")
            time.sleep(60)
        time.sleep(self.config.delay_between_comments_sec)

    def get_status(self) -> dict:
        self._prune_old_entries()
        return {
            "hourly_used": len(self._hourly_timestamps),
            "hourly_limit": self.config.max_comments_per_hour,
            "daily_used": len(self._daily_timestamps),
            "daily_limit": self.config.max_comments_per_day,
        }

    def _prune_old_entries(self):
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        while self._hourly_timestamps and self._hourly_timestamps[0] < hour_ago:
            self._hourly_timestamps.popleft()
        while self._daily_timestamps and self._daily_timestamps[0] < day_ago:
            self._daily_timestamps.popleft()
