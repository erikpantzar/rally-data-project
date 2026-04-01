from __future__ import annotations
from urllib.parse import urlparse
from fastapi import HTTPException

from app.scrapers.base import BaseScraper


# Populated by each scraper module via register()
_REGISTRY: dict[str, type[BaseScraper]] = {}


def register(domain: str):
    """Decorator to register a scraper class for a domain."""
    def decorator(cls: type[BaseScraper]) -> type[BaseScraper]:
        _REGISTRY[domain] = cls
        return cls
    return decorator


def get_scraper(url: str) -> BaseScraper:
    domain = urlparse(url).netloc.removeprefix("www.")
    scraper_cls = _REGISTRY.get(domain)
    if scraper_cls is None:
        supported = ", ".join(sorted(_REGISTRY.keys()))
        raise HTTPException(
            status_code=422,
            detail=f"No scraper registered for '{domain}'. Supported sites: {supported}",
        )
    return scraper_cls()
