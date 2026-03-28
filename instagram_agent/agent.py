"""Main agent orchestrator - ties everything together."""

import logging
import random
import time

import schedule

from .comments import CommentGenerator
from .config import AgentConfig
from .facebook_client import FacebookClient
from .instagram_service import InstagramService
from .rate_limiter import RateLimiter
from .targeting import TargetCandidate, TargetingEngine

logger = logging.getLogger(__name__)


class InstagramAgent:
    """Automated Instagram commenting agent."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = FacebookClient(config.credentials)
        self.service = InstagramService(self.client, config.credentials.instagram_account_id)
        self.targeting = TargetingEngine(self.service)
        self.rate_limiter = RateLimiter(config.rate_limit)
        self._comment_generators: dict[str, CommentGenerator] = {}
        self._setup_generators()

    def _setup_generators(self):
        for rule in self.config.targeting_rules:
            templates = rule.comment_templates if rule.comment_templates else None
            self._comment_generators[rule.name] = CommentGenerator(templates)

    def run_once(self) -> dict:
        """Execute a single pass: find targets and comment."""
        logger.info("=== Starting agent run ===")

        # Verify token
        try:
            me = self.client.verify_token()
            logger.info(f"Authenticated as: {me.get('name', 'Unknown')}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {"status": "error", "message": str(e)}

        # Find candidates
        candidates = self.targeting.find_candidates(self.config.targeting_rules)
        logger.info(f"Found {len(candidates)} candidates")

        # Shuffle to avoid patterns
        random.shuffle(candidates)

        commented = 0
        skipped = 0
        errors = 0

        for candidate in candidates:
            if not self.rate_limiter.can_proceed():
                logger.info("Rate limit reached, stopping this run")
                break

            success = self._process_candidate(candidate)
            if success:
                commented += 1
                self.rate_limiter.record_action()
                self.rate_limiter.wait_if_needed()
            elif success is None:
                skipped += 1
            else:
                errors += 1

        result = {
            "status": "ok",
            "candidates_found": len(candidates),
            "commented": commented,
            "skipped": skipped,
            "errors": errors,
            "rate_limit": self.rate_limiter.get_status(),
        }
        logger.info(f"=== Run complete: {result} ===")
        return result

    def _process_candidate(self, candidate: TargetCandidate) -> bool | None:
        """Process a single candidate. Returns True/False/None (skip)."""
        rule = candidate.rule
        generator = self._comment_generators.get(rule.name, CommentGenerator())

        # Pick context from the rule
        city = rule.locations[0] if rule.locations else ""
        hashtag = rule.hashtags[0] if rule.hashtags else ""

        comment = generator.generate(
            username=candidate.username,
            city=city,
            name=rule.name,
            hashtag=hashtag,
        )

        if self.config.dry_run:
            logger.info(f"[DRY RUN] Would comment on {candidate}: {comment}")
            return None

        try:
            result = self.service.comment_on_media(candidate.media_id, comment)
            logger.info(f"Commented on {candidate.permalink}: {comment}")
            return True
        except Exception as e:
            logger.error(f"Failed to comment on {candidate}: {e}")
            return False

    def run_scheduled(self, interval_minutes: int = 60):
        """Run the agent on a recurring schedule."""
        logger.info(f"Starting scheduled mode (every {interval_minutes} min)")

        schedule.every(interval_minutes).minutes.do(self._scheduled_run)

        # Run immediately on start
        self._scheduled_run()

        while True:
            schedule.run_pending()
            time.sleep(1)

    def _scheduled_run(self):
        try:
            self.targeting.reset()
            self.run_once()
        except Exception as e:
            logger.error(f"Scheduled run failed: {e}")
