"""Command line entry point for journalbot."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List

from .config import BotConfig, load_config
from .feeds import Entry, fetch_latest_entries
from .message import build_digest_message
from .telegram import TelegramClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _collect_entries(config: BotConfig, limit_override: int | None = None):
    for journal in config.journals:
        limit = limit_override or journal.max_items or config.items_per_journal
        logger.info("Fetching %s (limit=%s)", journal.name, limit)
        try:
            entries = fetch_latest_entries(journal.feed_url, limit)
        except Exception as exc:  # noqa: BLE001 - ensure we report the failure but keep the run going
            logger.error("Failed to fetch %s: %s", journal.name, exc)
            error_entry = Entry(title=f'⚠️ Error fetching feed: {exc}', link=journal.feed_url)
            yield journal.name, [error_entry]
        else:
            yield journal.name, entries


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send the latest journal posts via Telegram")
    parser.add_argument(
        "--config",
        default="journals.yaml",
        type=Path,
        help="Path to the YAML configuration file (default: journals.yaml)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Override the number of items per journal",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the message instead of sending it via Telegram",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Telegram bot token (defaults to TELEGRAM_BOT_TOKEN env variable)",
    )
    parser.add_argument(
        "--chat-id",
        default=None,
        help="Telegram chat ID (defaults to TELEGRAM_CHAT_ID env variable)",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except Exception as exc:  # noqa: BLE001 - surface config errors to the CLI
        parser.error(str(exc))

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be positive when provided")

    token = args.token or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = args.chat_id or os.environ.get("TELEGRAM_CHAT_ID")

    if not args.dry_run and (not token or not chat_id):
        parser.error("Telegram token and chat id must be provided via args or environment")

    journal_entries = list(_collect_entries(config, args.limit))
    message = build_digest_message(journal_entries)

    if args.dry_run:
        print(message)
        return 0

    client = TelegramClient(token=token, chat_id=chat_id)
    try:
        client.send_message(message)
    except Exception as exc:  # noqa: BLE001 - allow CLI to report the failure
        logger.error("Failed to send Telegram message: %s", exc)
        return 1

    logger.info("Digest delivered successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
