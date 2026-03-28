#!/usr/bin/env python3
"""CLI entry point for Instagram Agent."""

import argparse
import json
import logging
import sys

from instagram_agent.agent import InstagramAgent
from instagram_agent.config import AgentConfig


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    parser = argparse.ArgumentParser(
        description="Instagram Agent - Automated commenting via Facebook Graph API"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to targeting config JSON file (default: config.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without posting comments (simulation mode)",
    )
    parser.add_argument(
        "--schedule",
        type=int,
        default=0,
        metavar="MINUTES",
        help="Run on a schedule every N minutes (0 = run once)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify credentials and exit",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show account info and exit",
    )

    args = parser.parse_args()

    config = AgentConfig.load(args.config)
    config.dry_run = args.dry_run

    setup_logging(config.log_level)
    logger = logging.getLogger("instagram_agent")

    # Validate credentials
    errors = config.credentials.validate()
    if errors:
        for err in errors:
            logger.error(err)
        logger.error("Set the required environment variables in .env (see .env.example)")
        sys.exit(1)

    agent = InstagramAgent(config)

    if args.verify:
        try:
            info = agent.client.verify_token()
            print(f"Token valid. Authenticated as: {info.get('name', 'N/A')}")
        except Exception as e:
            print(f"Token invalid: {e}")
            sys.exit(1)
        return

    if args.status:
        try:
            info = agent.service.get_account_info()
            print(json.dumps(info, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Could not fetch account info: {e}")
            sys.exit(1)
        return

    if not config.targeting_rules:
        logger.warning("No targeting rules configured. Create a config.json file.")
        logger.info("See config.example.json for an example configuration.")
        sys.exit(1)

    if args.schedule > 0:
        agent.run_scheduled(args.schedule)
    else:
        result = agent.run_once()
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
