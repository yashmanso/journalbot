"""Configuration helpers for journalbot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional

import yaml


@dataclass
class JournalConfig:
    """Configuration for a single journal feed."""

    name: str
    feed_url: str
    max_items: Optional[int] = None


@dataclass
class BotConfig:
    """Top level configuration for the bot."""

    journals: List[JournalConfig]
    items_per_journal: int = 5

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BotConfig":
        journals_data = data.get("journals", [])
        if not isinstance(journals_data, Iterable) or isinstance(journals_data, (str, bytes)):
            raise ValueError("'journals' must be a list of objects")

        journals: List[JournalConfig] = []
        for index, item in enumerate(journals_data):
            if not isinstance(item, dict):
                raise ValueError(f"Journal entry at index {index} must be a mapping")

            name = item.get("name")
            feed_url = item.get("feed_url") or item.get("rss")
            if not name or not feed_url:
                raise ValueError(
                    "Each journal must include both 'name' and 'feed_url' (or 'rss') fields"
                )

            max_items = item.get('max_items')
            if max_items is None:
                max_items = item.get('items')
            if max_items is not None:
                try:
                    max_items_int = int(max_items)
                except (TypeError, ValueError) as exc:
                    raise ValueError('max_items must be an integer when provided') from exc
                if max_items_int <= 0:
                    raise ValueError('max_items must be a positive integer when provided')
                max_items = max_items_int

            journals.append(JournalConfig(name=str(name), feed_url=str(feed_url), max_items=max_items))

        if not journals:
            raise ValueError("At least one journal must be configured")

        items_per_journal = data.get("items_per_journal", 5)
        try:
            items_per_journal = int(items_per_journal)
        except (TypeError, ValueError) as exc:
            raise ValueError("items_per_journal must be an integer") from exc
        if items_per_journal <= 0:
            raise ValueError("items_per_journal must be positive")

        return cls(journals=journals, items_per_journal=items_per_journal)


def load_config(path: str | Path) -> BotConfig:
    """Load configuration from a YAML file."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a mapping")

    return BotConfig.from_dict(data)
