"""スポット閲覧やお気に入り操作に関するサービス関数群。"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.db.models import F
from django.utils import timezone

from ..models import Spot, SpotView, UserProfile, UserSpotInteraction

logger = logging.getLogger(__name__)


def log_spot_view(spot: Spot, user: Any) -> None:
    """閲覧ログとユーザーごとの閲覧回数を記録する。"""

    try:
        SpotView.objects.create(spot=spot)
    except Exception:  # pragma: no cover - ログ記録失敗は致命的ではない
        logger.exception("Failed to store SpotView log", extra={"spot_id": spot.id})

    if not getattr(user, "is_authenticated", False):
        return

    try:
        interaction, created = UserSpotInteraction.objects.get_or_create(
            user=user,
            spot=spot,
            defaults={"view_count": 1},
        )
        if not created:
            UserSpotInteraction.objects.filter(pk=interaction.pk).update(
                view_count=F("view_count") + 1,
                last_viewed_at=timezone.now(),
            )
    except Exception:  # pragma: no cover - 分析データの記録失敗は無視
        logger.exception(
            "Failed to update user spot interaction",
            extra={"spot_id": spot.id, "user_id": getattr(user, "id", None)},
        )


def update_view_duration(spot: Spot, user: Any, duration: timedelta) -> None:
    """スポット滞在時間を更新する。"""

    if not getattr(user, "is_authenticated", False):
        return

    normalized_duration = duration if duration > timedelta(0) else timedelta(0)

    try:
        interaction, created = UserSpotInteraction.objects.get_or_create(
            user=user,
            spot=spot,
            defaults={
                "view_count": 1,
                "total_view_duration": normalized_duration,
            },
        )
        if created or normalized_duration == timedelta(0):
            return

        UserSpotInteraction.objects.filter(pk=interaction.pk).update(
            total_view_duration=F("total_view_duration") + normalized_duration,
            last_viewed_at=timezone.now(),
        )
    except Exception:  # pragma: no cover - 分析データの記録失敗は無視
        logger.exception(
            "Failed to update view duration",
            extra={"spot_id": spot.id, "user_id": getattr(user, "id", None)},
        )


def is_favorite_spot(spot: Spot, user: Any) -> bool:
    """指定スポットがお気に入り登録されているか判定する。"""

    if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return False

    return UserProfile.objects.filter(user=user, favorite_spots=spot).exists()


def toggle_favorite_spot(spot: Spot, user: Any) -> bool:
    """お気に入り状態をトグルし、新しい状態を返す。"""

    if not getattr(user, "is_authenticated", False):
        raise ValueError("toggle_favorite_spot requires an authenticated user")

    profile, _ = UserProfile.objects.get_or_create(user=user)
    if profile.favorite_spots.filter(pk=spot.pk).exists():
        profile.favorite_spots.remove(spot)
        return False

    profile.favorite_spots.add(spot)
    return True


def fetch_related_spots(spot: Spot, limit: int = 5):
    """同じユーザーが投稿した関連スポットを取得する。"""

    return (
        spot.created_by.spot_set.exclude(id=spot.id)
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")[:limit]
    )
