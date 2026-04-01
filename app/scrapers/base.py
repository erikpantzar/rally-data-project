from __future__ import annotations
from abc import ABC, abstractmethod

import httpx


class BaseScraper(ABC):
    """Fetch a URL and parse it into a structured dict."""

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            response = await client.get(
                url,
                headers={"User-Agent": "rally-data-bot/0.1 (+https://github.com/local/rally-data-project)"},
            )
            response.raise_for_status()
            return response.text

    @abstractmethod
    def parse(self, html: str, url: str) -> dict:
        """Parse raw HTML into a structured dict matching one of the app.models shapes."""

    async def scrape(self, url: str) -> dict:
        html = await self.fetch(url)
        return self.parse(html, url)
