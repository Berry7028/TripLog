"""ビューで利用するシリアライザ的ユーティリティ。"""

from __future__ import annotations

from typing import Dict

from ..models import Review, Spot, UserProfile


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


def serialize_spot_detail(spot: Spot) -> Dict[str, object]:
    """スポット詳細向けの情報。"""

    image_url = _resolve_image_url(spot)
    created_by_username = spot.created_by.username if spot.created_by_id else "匿名"
    return {
        "id": spot.id,
        "title": spot.title,
        "description": spot.description,
        "latitude": spot.latitude,
        "longitude": spot.longitude,
        "address": spot.address,
        "image": image_url,
        "created_by": created_by_username,
        "created_by_detail": {
            "id": spot.created_by.id if spot.created_by_id else None,
            "username": created_by_username,
        },
        "created_at": spot.created_at.isoformat() if spot.created_at else None,
        "updated_at": spot.updated_at.isoformat() if spot.updated_at else None,
        "tags": [tag.name for tag in spot.tags.all()],
        "is_ai_generated": spot.is_ai_generated,
    }


def serialize_review(review: Review) -> Dict[str, object]:
    """レビュー情報をJSON化。"""

    return {
        "id": review.id,
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at.isoformat() if review.created_at else None,
        "user": {
            "id": review.user.id,
            "username": review.user.username,
        },
    }


def serialize_user_profile(profile: UserProfile) -> Dict[str, object]:
    """ユーザープロフィールをJSON化。"""

    avatar_url = None
    if profile.avatar:
        try:
            avatar_url = profile.avatar.url
        except Exception:
            avatar_url = None

    return {
        "bio": profile.bio,
        "avatar": avatar_url,
        "favorite_spots": [serialize_spot_summary(spot) for spot in profile.favorite_spots.all()],
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
