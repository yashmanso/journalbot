"""Message formatting helpers."""

from __future__ import annotations

import html
from typing import Iterable

from .feeds import Entry


def _format_entry(entry: Entry) -> str:
    title = html.escape(entry.title)
    link = html.escape(entry.link, quote=True)
    pieces = [f"&bull; <a href=\"{link}\">{title}</a>"]
    if entry.published:
        pieces.append(f" <i>({entry.published.strftime('%Y-%m-%d')})</i>")
    return "".join(pieces)


def build_digest_message(journal_entries: Iterable[tuple[str, list[Entry]]]) -> str:
    """Build an HTML formatted message for Telegram."""

    sections = []
    for journal_name, entries in journal_entries:
        title = html.escape(journal_name)
        sections.append(f"<b>{title}</b>")
        if entries:
            sections.extend(_format_entry(entry) for entry in entries)
        else:
            sections.append("&bull; No recent entries found")

    return "\n".join(sections)
