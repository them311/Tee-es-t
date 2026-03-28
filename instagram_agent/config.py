"""Configuration module - loads settings from .env and config files."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class FacebookCredentials:
    app_id: str = ""
    app_secret: str = ""
    access_token: str = ""
    instagram_account_id: str = ""

    @classmethod
    def from_env(cls) -> "FacebookCredentials":
        return cls(
            app_id=os.getenv("FACEBOOK_APP_ID", ""),
            app_secret=os.getenv("FACEBOOK_APP_SECRET", ""),
            access_token=os.getenv("FACEBOOK_ACCESS_TOKEN", ""),
            instagram_account_id=os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", ""),
        )

    def validate(self) -> list[str]:
        errors = []
        if not self.access_token:
            errors.append("FACEBOOK_ACCESS_TOKEN is required")
        if not self.instagram_account_id:
            errors.append("INSTAGRAM_BUSINESS_ACCOUNT_ID is required")
        return errors


@dataclass
class RateLimitConfig:
    max_comments_per_hour: int = 20
    max_comments_per_day: int = 100
    delay_between_comments_sec: int = 30

    @classmethod
    def from_env(cls) -> "RateLimitConfig":
        return cls(
            max_comments_per_hour=int(os.getenv("MAX_COMMENTS_PER_HOUR", "20")),
            max_comments_per_day=int(os.getenv("MAX_COMMENTS_PER_DAY", "100")),
            delay_between_comments_sec=int(os.getenv("DELAY_BETWEEN_COMMENTS_SEC", "30")),
        )


@dataclass
class TargetingRule:
    """A single targeting rule for filtering posts."""
    name: str = ""
    hashtags: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    usernames: list[str] = field(default_factory=list)
    comment_templates: list[str] = field(default_factory=list)

    def matches_text(self, text: str) -> bool:
        text_lower = text.lower()
        if self.keywords:
            if any(kw.lower() in text_lower for kw in self.keywords):
                return True
        if self.hashtags:
            if any(tag.lower() in text_lower for tag in self.hashtags):
                return True
        if self.locations:
            if any(loc.lower() in text_lower for loc in self.locations):
                return True
        if not self.keywords and not self.hashtags and not self.locations:
            return True
        return False


@dataclass
class AgentConfig:
    credentials: FacebookCredentials = field(default_factory=FacebookCredentials)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    targeting_rules: list[TargetingRule] = field(default_factory=list)
    log_level: str = "INFO"
    dry_run: bool = False

    @classmethod
    def load(cls, config_path: str | None = None) -> "AgentConfig":
        config = cls(
            credentials=FacebookCredentials.from_env(),
            rate_limit=RateLimitConfig.from_env(),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )

        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                data = json.load(f)
            for rule_data in data.get("targeting_rules", []):
                config.targeting_rules.append(TargetingRule(**rule_data))

        return config
