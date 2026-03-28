"""Instagram Business API service - media discovery, commenting, interactions."""

import logging

from .facebook_client import FacebookClient

logger = logging.getLogger(__name__)


class InstagramService:
    """High-level Instagram operations via Facebook Graph API."""

    def __init__(self, client: FacebookClient, ig_account_id: str):
        self.client = client
        self.ig_account_id = ig_account_id

    def get_account_info(self) -> dict:
        """Get Instagram business account details."""
        return self.client.get(
            self.ig_account_id,
            params={"fields": "id,username,name,biography,followers_count,media_count"},
        )

    def search_hashtag(self, hashtag: str) -> str | None:
        """Search for a hashtag ID by name."""
        data = self.client.get("ig_hashtag_search", params={
            "user_id": self.ig_account_id,
            "q": hashtag.lstrip("#"),
        })
        hashtags = data.get("data", [])
        return hashtags[0]["id"] if hashtags else None

    def get_hashtag_recent_media(self, hashtag_id: str, limit: int = 20) -> list[dict]:
        """Get recent media for a hashtag."""
        data = self.client.get(
            f"{hashtag_id}/recent_media",
            params={
                "user_id": self.ig_account_id,
                "fields": "id,caption,media_type,permalink,timestamp,username",
                "limit": limit,
            },
        )
        return data.get("data", [])

    def get_hashtag_top_media(self, hashtag_id: str) -> list[dict]:
        """Get top media for a hashtag."""
        data = self.client.get(
            f"{hashtag_id}/top_media",
            params={
                "user_id": self.ig_account_id,
                "fields": "id,caption,media_type,permalink,timestamp,username",
            },
        )
        return data.get("data", [])

    def get_user_media(self, limit: int = 20) -> list[dict]:
        """Get the business account's own recent media."""
        data = self.client.get(
            f"{self.ig_account_id}/media",
            params={
                "fields": "id,caption,media_type,permalink,timestamp,like_count,comments_count",
                "limit": limit,
            },
        )
        return data.get("data", [])

    def get_media_comments(self, media_id: str, limit: int = 50) -> list[dict]:
        """Get comments on a specific media."""
        data = self.client.get(
            f"{media_id}/comments",
            params={
                "fields": "id,text,timestamp,username",
                "limit": limit,
            },
        )
        return data.get("data", [])

    def comment_on_media(self, media_id: str, message: str) -> dict:
        """Post a comment on a media object."""
        logger.info(f"Commenting on media {media_id}: {message[:50]}...")
        return self.client.post(
            f"{media_id}/comments",
            data={"message": message},
        )

    def reply_to_comment(self, comment_id: str, message: str) -> dict:
        """Reply to a specific comment."""
        logger.info(f"Replying to comment {comment_id}: {message[:50]}...")
        return self.client.post(
            f"{comment_id}/replies",
            data={"message": message},
        )

    def get_mentioned_media(self, limit: int = 20) -> list[dict]:
        """Get media where the business account is mentioned."""
        data = self.client.get(
            f"{self.ig_account_id}/tags",
            params={
                "fields": "id,caption,media_type,permalink,timestamp,username",
                "limit": limit,
            },
        )
        return data.get("data", [])

    def discover_user(self, username: str) -> dict | None:
        """Discover a business/creator user by username."""
        try:
            data = self.client.get(
                f"{self.ig_account_id}",
                params={
                    "fields": f"business_discovery.fields(id,username,name,biography,media_count,followers_count,media.limit(10){{id,caption,media_type,permalink,timestamp}}).username({username})",
                },
            )
            return data.get("business_discovery")
        except Exception as e:
            logger.warning(f"Could not discover user @{username}: {e}")
            return None
