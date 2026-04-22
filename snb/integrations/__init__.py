"""External SaaS connectors.

Each integration exposes a thin, async, typed client. Business logic lives
in snb.services, NOT here — integrations stay replaceable.
"""

from snb.integrations.base import BaseIntegration

__all__ = ["BaseIntegration"]
