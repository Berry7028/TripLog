"""ビューで利用するシリアライザ的ユーティリティ。"""

from __future__ import annotations

from typing import Dict

from ..models import Spot


def serialize_spot_summary(spot: Spot) -> Dict[str, object]:
    """一覧やAPIレスポンス向けのスポット情報。"""

    image_url = _resolve_image_url(spot)
    return {
        "id": spot.id,
        "title": spot.title,
        "description": spot.description,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
        "address": spot.address,
        "image": image_url,
        "created_by": spot.created_by.username,
        "created_at": spot.created_at.isoformat() if spot.created_at else None,
        "tags": [tag.name for tag in spot.tags.all()],
    }


def serialize_spot_brief(spot: Spot) -> Dict[str, object]:
    """検索候補などに使うコンパクトな表現。"""

    return {
        "id": spot.id,
        "title": spot.title,
        "address": spot.address,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
    }


def _resolve_image_url(spot: Spot) -> str | None:
    if spot.image:
        try:
            return spot.image.url
        except Exception:
            pass
    return spot.image_url or None
