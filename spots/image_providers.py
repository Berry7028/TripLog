"""画像取得に関するユーティリティ。"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional
from urllib.parse import quote_plus

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
SOURCE_UNSPLASH_URL = "https://source.unsplash.com/featured/"
DEFAULT_UNSPLASH_TIMEOUT = 5
DEFAULT_UNSPLASH_FALLBACK_QUERY = "travel"


def _get_unsplash_access_key() -> Optional[str]:
    """設定から Unsplash のアクセストークンを取得する。"""
    key = getattr(settings, "UNSPLASH_ACCESS_KEY", None)
    if key:
        key = key.strip()
    return key or None


@lru_cache(maxsize=128)
def fetch_unsplash_image(query: str) -> Optional[str]:
    """指定したクエリで Unsplash から画像 URL を取得する。"""
    if not query:
        return None

    access_key = _get_unsplash_access_key()
    if not access_key:
        return None

    timeout = getattr(settings, "UNSPLASH_TIMEOUT", DEFAULT_UNSPLASH_TIMEOUT)
    orientation = getattr(settings, "UNSPLASH_DEFAULT_ORIENTATION", "landscape")

    params = {
        "query": query,
        "per_page": 1,
        "orientation": orientation,
    }
    headers = {
        "Authorization": f"Client-ID {access_key}",
        "Accept-Version": "v1",
    }

    try:
        response = requests.get(UNSPLASH_SEARCH_URL, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:  # pragma: no cover - ネットワーク例外はログのみ
        logger.warning("Unsplash API からの画像取得に失敗しました: %s", exc)
        return None

    try:
        data = response.json()
    except ValueError as exc:  # pragma: no cover - JSON 以外のレスポンス
        logger.warning("Unsplash API のレスポンスが JSON ではありません: %s", exc)
        return None

    results = data.get("results") or []
    if not results:
        return None

    urls = results[0].get("urls") or {}
    for size_key in ("regular", "small", "full", "thumb"):
        image_url = urls.get(size_key)
        if image_url:
            return image_url

    return None


def get_spot_fallback_image(title: str) -> Optional[str]:
    """スポット名をもとに Unsplash からフォールバック画像を取得する。"""
    sanitized_title = (title or "").strip()

    api_result = fetch_unsplash_image(sanitized_title)
    if api_result:
        return api_result

    return _build_source_unsplash_url(sanitized_title)


def _build_source_unsplash_url(query: str) -> Optional[str]:
    """Unsplash Source (非 API) の URL を生成する。"""
    fallback_query = getattr(settings, "UNSPLASH_FALLBACK_QUERY", DEFAULT_UNSPLASH_FALLBACK_QUERY)

    sanitized_query = " ".join((query or "").split())
    if not sanitized_query:
        sanitized_query = fallback_query.strip()

    if not sanitized_query:
        return None

    encoded_query = quote_plus(sanitized_query)
    orientation = (getattr(settings, "UNSPLASH_DEFAULT_ORIENTATION", "") or "").strip()

    if orientation:
        return f"{SOURCE_UNSPLASH_URL}?{encoded_query}&orientation={quote_plus(orientation)}"

    return f"{SOURCE_UNSPLASH_URL}?{encoded_query}"
