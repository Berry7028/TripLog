"""ユーザー閲覧データを活用したレコメンドロジック。"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Set

from django.utils import timezone

from ..models import UserSpotInteraction

logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """並び替え結果とメタ情報を保持するデータクラス。"""

    spots: List
    source: str = 'none'  # 'api' | 'fallback' | 'none' のいずれかを示す
    scored_spot_ids: Set[int] = field(default_factory=set)
    scores: Dict[int, float] = field(default_factory=dict)


def order_spots_by_relevance(spots: Sequence, user) -> RecommendationResult:
    """ユーザーの閲覧傾向に基づいてスポットを並び替える。"""

    spots_list = list(spots)
    if not spots_list or user is None or not getattr(user, 'is_authenticated', False):
        return RecommendationResult(spots_list)

    spot_ids = [spot.id for spot in spots_list]
    interactions = list(
        UserSpotInteraction.objects.filter(user=user, spot_id__in=spot_ids)
        .select_related('spot')
        .prefetch_related('spot__tags')
    )
    if not interactions:
        return RecommendationResult(spots_list)

    fallback_scores = {
        interaction.spot_id: _compute_fallback_score(interaction)
        for interaction in interactions
    }
    if not any(score > 0 for score in fallback_scores.values()):
        return RecommendationResult(spots_list)

    scores = {
        spot_id: round(float(score_value), 4)
        for spot_id, score_value in fallback_scores.items()
    }

    min_score = min(scores.values())
    default_score = min_score - 0.001

    def sort_key(spot):
        return (
            scores.get(spot.id, default_score),
            spot.created_at,
        )

    sorted_spots = sorted(spots_list, key=sort_key, reverse=True)
    return RecommendationResult(
        sorted_spots,
        source='fallback',
        scored_spot_ids=set(scores.keys()),
        scores=scores,
    )


def _compute_fallback_score(interaction: UserSpotInteraction) -> float:
    """APIが利用できない場合のスコア計算ロジック。"""

    duration_seconds = interaction.total_view_duration.total_seconds()
    duration_minutes = duration_seconds / 60.0
    view_bonus = interaction.view_count * 2.0

    recency_delta = timezone.now() - interaction.last_viewed_at
    recency_days = max(recency_delta.total_seconds() / 86400.0, 0.0)
    # 直近30日以内の閲覧に重み付け
    recency_bonus = max(0.0, 3.0 - (recency_days / 10.0))

    duration_bonus = min(duration_minutes, 60.0) * 0.5

    return round(view_bonus + recency_bonus + duration_bonus, 4)



