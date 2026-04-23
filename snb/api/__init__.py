"""FastAPI application factory.

Lazy-imports FastAPI so the base package stays dependency-light. Install the
``api`` extra to use it: ``pip install -e '.[api]'``.
"""

from snb.api.app import create_app

__all__ = ["create_app"]
