"""Command-line entry point: `studentflow run-agents`, `studentflow run-api`."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys

from .agents import run_forever
from .config import get_settings
from .db import InMemoryRepository, Repository, SupabaseRepository


def _build_repo() -> Repository:
    settings = get_settings()
    if settings.supabase_configured:
        return SupabaseRepository(settings)
    logging.warning("Supabase not configured — falling back to in-memory repository")
    return InMemoryRepository()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="studentflow")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("run-agents", help="Start the 3 agent loops")

    run_api = sub.add_parser("run-api", help="Start the FastAPI server")
    run_api.add_argument("--host", default=None)
    run_api.add_argument("--port", type=int, default=None)

    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )

    if args.command == "run-agents":
        repo = _build_repo()
        asyncio.run(run_forever(repo))
        return 0

    if args.command == "run-api":
        import uvicorn

        settings = get_settings()
        uvicorn.run(
            "studentflow.api:app",
            host=args.host or settings.api_host,
            port=args.port or settings.api_port,
            reload=False,
        )
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
