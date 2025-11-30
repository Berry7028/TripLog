from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

UNSPLASH_ENDPOINT = "https://api.unsplash.com/search/photos"
WIKIPEDIA_ENDPOINT = "https://ja.wikipedia.org/api/rest_v1/page/summary/{title}"

@dataclass
class ImageLookupResult:
    url: str
    attribution: Optional[str] = None

def fetch_spot_image(*, title: str, description: str = "", latitude: float | None = None,longitude: float | None = None) -> Optional[ImageLookupResult]:
    """Unsplash → Wikipedia の順で URL を探す。未取得なら None を返す。"""
    if getattr(settings, "IMAGE_LOOKUP_ENABLED", False):
        url = _fetch_from_unsplash(title=title, description=description)
        if url:
            return ImageLookupResult(url=url, attribution="Unsplash")
    else:
        logger.info("Image lookup disabled via settings.")

    wiki_url = _fetch_from_wikipedia(title)
    if wiki_url:
        return ImageLookupResult(url=wiki_url, attribution="Wikipedia")
    return None

def _fetch_from_unsplash(*, title:str, description: str) -> Optional[str]:
    if not settings.UNSPLASH_ACCESS_KEY:
        return None
    query = title or description or "travel spot"
    params = {"query": query, "orientation": "landscape", "per_page": 1}
    headers = {"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"}
    try:
        resp = requests.get(UNSPLASH_ENDPOINT, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Unsplash lookup failed: %s", exc)
        return None
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    first = results[0]
    return first.get("urls", {}).get("regular")

def _fetch_from_wikipedia(title: str) -> Optional[str]:
    if not title:
        return None
    try:
        resp= requests.get(WIKIPEDIA_ENDPOINT.format(title=title), timeout=5)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Wikipedia lookup failed: %s", exc)
        return None
    data = resp.json()
    thumbnail = data.get("thumbnail") or {}
    source = thumbnail.get("source")
    return source if source and source.startswith("http://") else None