"""Journal bot package."""

from .config import BotConfig, JournalConfig, load_config
from .feeds import Entry, fetch_latest_entries
from .message import build_digest_message
from .telegram import TelegramClient

__all__ = [
    "BotConfig",
    "JournalConfig",
    "load_config",
    "Entry",
    "fetch_latest_entries",
    "build_digest_message",
    "TelegramClient",
]
