"""SNB — core automation, agent and integration package.

Modular foundation for SNB Consulting operational systems:
- agents: autonomous orchestration
- core: base classes, retries, exceptions
- config: settings and logging
- integrations: external SaaS connectors (Gmail, Airtable, HubSpot, Shopify, ...)
- pipelines: composable data flows
- scrapers: resilient extraction
- services: business-facing domain logic
- utils: shared helpers
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("snb")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["__version__"]
