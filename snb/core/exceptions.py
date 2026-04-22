"""Domain exception hierarchy. Integrations raise subclasses so callers can
handle transport-level vs business-level failures distinctly.
"""

from __future__ import annotations


class SnbError(Exception):
    """Root exception for everything thrown by this package."""


class IntegrationError(SnbError):
    """External system returned an unexpected response."""


class RetryableError(SnbError):
    """Operation failed but retrying may succeed."""


class TransientError(RetryableError):
    """Network / 5xx / timeout class failures."""


class RateLimitError(RetryableError):
    def __init__(self, message: str = "rate limited", retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class NotFoundError(SnbError):
    """Resource addressed does not exist."""


class AuthError(SnbError):
    """Missing or invalid credentials."""


class ValidationError(SnbError):
    """Payload failed local validation before hitting the wire."""
