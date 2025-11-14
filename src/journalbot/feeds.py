"""Feed fetching utilities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

import feedparser


@dataclass
class Entry:
    """A single feed entry."""

    title: str
    link: str
    published: Optional[datetime] = None


def _to_datetime(struct_time) -> Optional[datetime]:
    if struct_time is None:
        return None

    try:
        return datetime(
            year=struct_time.tm_year,
            month=struct_time.tm_mon,
            day=struct_time.tm_mday,
            hour=struct_time.tm_hour,
            minute=struct_time.tm_min,
            second=struct_time.tm_sec,
            tzinfo=timezone.utc,
        )
    except Exception:
        return None


def fetch_latest_entries(feed_url: str, limit: int) -> List[Entry]:
    """Fetch the latest entries from a feed."""

    parsed = feedparser.parse(feed_url)
    if getattr(parsed, "bozo", False):
        exception = getattr(parsed, "bozo_exception", None)
        if exception is not None:
            raise RuntimeError(f"Failed to parse feed {feed_url}: {exception}")
        raise RuntimeError(f"Failed to parse feed {feed_url}")

    entries: List[Entry] = []
    for entry in parsed.entries[:limit]:
        title = entry.get("title") or "Untitled"
        link = entry.get("link") or feed_url
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        entries.append(Entry(title=title, link=link, published=_to_datetime(published)))

    return entries
