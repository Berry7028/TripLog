"""画像取得に関するユーティリティ。"""

from __future__ import annotations

import hashlib
import logging
from functools import lru_cache
from typing import Optional, Tuple
from urllib.parse import quote_plus, urlencode

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"
SOURCE_UNSPLASH_URL = "https://source.unsplash.com/featured/"
STATIC_UNSPLASH_IMAGE_BASE = "https://images.unsplash.com"
DEFAULT_UNSPLASH_TIMEOUT = 5
DEFAULT_UNSPLASH_FALLBACK_QUERY = "travel"
DEFAULT_UNSPLASH_SIZE = "480x240"
DEFAULT_UNSPLASH_IMAGE_QUALITY = 80

# Unsplash の人気トラベル写真（Unsplash ライセンス対応）。
# 公式の hotlink ガイドラインに従い images.unsplash.com を使用します。
# https://help.unsplash.com/api-guidelines/guideline-hotlinking-images
STATIC_UNSPLASH_IMAGE_IDS = (
    "photo-1500530855697-b586d89ba3ee",
    "photo-1526772662000-3f88f10405ff",
    "photo-1469474968028-56623f02e42e",
    "photo-1507525428034-b723cf961d3e",
    "photo-1496307042754-b4aa456c4a2d",
    "photo-1470071459604-3b5ec3a7fe05",
    "photo-1467269204594-9661b134dd2b",
    "photo-1491553895911-0055eca6402d",
    "photo-1512453979798-5ea266f8880c",
    "photo-1433838552652-f9a46b332c40",
)
def _parse_unsplash_size(size_value: Optional[str]) -> Tuple[int, int]:
    """"480x240" のようなサイズ文字列を (width, height) へ変換する。"""

    size_str = (size_value or "").strip().lower() or DEFAULT_UNSPLASH_SIZE
    try:
        width_str, height_str = size_str.split("x", 1)
        width = int(width_str)
        height = int(height_str)
        if width > 0 and height > 0:
            return width, height
    except (ValueError, TypeError):
        pass

    # フォールバックとして既定値を返す
    return tuple(int(part) for part in DEFAULT_UNSPLASH_SIZE.split("x", 1))


def _build_static_unsplash_image(query: str) -> Optional[str]:
    """API キーなしで利用できる静的 Unsplash 画像を決定する。"""

    if not STATIC_UNSPLASH_IMAGE_IDS:
        return None

    sanitized_query = " ".join((query or "").split()) or DEFAULT_UNSPLASH_FALLBACK_QUERY
    hash_digest = hashlib.sha256(sanitized_query.encode("utf-8")).hexdigest()
    index = int(hash_digest[:8], 16) % len(STATIC_UNSPLASH_IMAGE_IDS)
    image_id = STATIC_UNSPLASH_IMAGE_IDS[index]

    width, height = _parse_unsplash_size(getattr(settings, "UNSPLASH_DEFAULT_SIZE", DEFAULT_UNSPLASH_SIZE))
    quality = getattr(settings, "UNSPLASH_FALLBACK_QUALITY", DEFAULT_UNSPLASH_IMAGE_QUALITY)

    params = {
        "auto": "format",
        "fit": "crop",
        "w": width,
        "h": height,
        "q": quality,
    }

    utm_source = getattr(settings, "UNSPLASH_UTM_SOURCE", "TripLog")
    if utm_source:
        params["utm_source"] = utm_source

    utm_medium = getattr(settings, "UNSPLASH_UTM_MEDIUM", "referral")
    if utm_medium:
        params["utm_medium"] = utm_medium

    return f"{STATIC_UNSPLASH_IMAGE_BASE}/{image_id}?{urlencode(params)}"



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

    if getattr(settings, "UNSPLASH_USE_SOURCE", False):
        source_url = _build_source_unsplash_url(sanitized_title)
        if source_url:
            return source_url

    return _build_static_unsplash_image(sanitized_title)


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
    size = (getattr(settings, "UNSPLASH_DEFAULT_SIZE", DEFAULT_UNSPLASH_SIZE) or "").strip()

    base_url = SOURCE_UNSPLASH_URL
    if size:
        base_url = f"{SOURCE_UNSPLASH_URL}{size}/"

    params = []
    if orientation:
        params.append(f"orientation={quote_plus(orientation)}")

    query_string = f"?{encoded_query}"
    if params:
        query_string += "&" + "&".join(params)

    return base_url + query_string
