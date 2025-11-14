"""Simple Telegram API client."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)


@dataclass
class TelegramClient:
    """Wrapper for sending messages via Telegram bot API."""

    token: str
    chat_id: str
    api_url: str = "https://api.telegram.org"
    timeout: int = 10

    def send_message(self, text: str, parse_mode: str = "HTML", disable_preview: bool = True) -> None:
        url = f"{self.api_url}/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_preview,
        }
        response = requests.post(url, data=payload, timeout=self.timeout)
        if response.status_code >= 400:
            logger.error("Telegram API error %s: %s", response.status_code, response.text)
            response.raise_for_status()

        logger.info("Message sent to chat %s", self.chat_id)
