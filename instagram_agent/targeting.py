"""Targeting engine - finds and filters posts based on rules."""

import logging

from .config import TargetingRule
from .instagram_service import InstagramService

logger = logging.getLogger(__name__)


class TargetCandidate:
    """A post that matched targeting criteria."""

    def __init__(self, media_id: str, caption: str, username: str,
                 permalink: str, rule: TargetingRule):
        self.media_id = media_id
        self.caption = caption
        self.username = username
        self.permalink = permalink
        self.rule = rule

    def __repr__(self) -> str:
        return f"<Target @{self.username} rule='{self.rule.name}' media={self.media_id}>"


class TargetingEngine:
    """Finds posts matching targeting rules."""

    def __init__(self, service: InstagramService):
        self.service = service
        self._already_seen: set[str] = set()

    def find_candidates(self, rules: list[TargetingRule]) -> list[TargetCandidate]:
        """Find all post candidates matching the given rules."""
        candidates = []

        for rule in rules:
            found = self._search_for_rule(rule)
            candidates.extend(found)
            logger.info(f"Rule '{rule.name}': found {len(found)} candidates")

        return candidates

    def _search_for_rule(self, rule: TargetingRule) -> list[TargetCandidate]:
        candidates = []

        # Search by hashtags
        for hashtag in rule.hashtags:
            media_list = self._search_by_hashtag(hashtag)
            for media in media_list:
                candidate = self._evaluate_media(media, rule)
                if candidate:
                    candidates.append(candidate)

        # Search by usernames (business discovery)
        for username in rule.usernames:
            media_list = self._search_by_username(username)
            for media in media_list:
                candidate = self._evaluate_media(media, rule)
                if candidate:
                    candidates.append(candidate)

        # If no hashtags/usernames, search mentions and own tagged media
        if not rule.hashtags and not rule.usernames:
            media_list = self._get_mentioned_media()
            for media in media_list:
                candidate = self._evaluate_media(media, rule)
                if candidate:
                    candidates.append(candidate)

        return candidates

    def _search_by_hashtag(self, hashtag: str) -> list[dict]:
        hashtag_id = self.service.search_hashtag(hashtag)
        if not hashtag_id:
            logger.warning(f"Hashtag #{hashtag} not found")
            return []

        recent = self.service.get_hashtag_recent_media(hashtag_id)
        top = self.service.get_hashtag_top_media(hashtag_id)

        all_media = {m["id"]: m for m in recent + top}
        return list(all_media.values())

    def _search_by_username(self, username: str) -> list[dict]:
        user_data = self.service.discover_user(username)
        if not user_data or "media" not in user_data:
            return []
        return user_data["media"].get("data", [])

    def _get_mentioned_media(self) -> list[dict]:
        try:
            return self.service.get_mentioned_media()
        except Exception as e:
            logger.warning(f"Could not fetch mentions: {e}")
            return []

    def _evaluate_media(self, media: dict, rule: TargetingRule) -> TargetCandidate | None:
        media_id = media.get("id", "")
        if media_id in self._already_seen:
            return None

        caption = media.get("caption", "")
        if not rule.matches_text(caption):
            return None

        self._already_seen.add(media_id)
        return TargetCandidate(
            media_id=media_id,
            caption=caption,
            username=media.get("username", "unknown"),
            permalink=media.get("permalink", ""),
            rule=rule,
        )

    def reset(self):
        """Clear the seen cache for a fresh run."""
        self._already_seen.clear()
