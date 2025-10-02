"""ホーム画面向けのスポット取得と並び替えロジック。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet

from ..models import Spot, UserRecommendationScore

ALLOWED_SORT_MODES = {"recent", "relevance"}
DEFAULT_SORT_MODE = "recent"


@dataclass
class HomepageSpotsResult:
    """ホーム画面に表示するスポットとメタ情報。"""

    spots: List[Spot]
    search_query: str
    sort_mode: str
    recommendation_source: str | None = None
    recommendation_notice: str | None = None
    recommendation_scored_ids: List[int] = field(default_factory=list)


def fetch_homepage_spots(
    *,
    user,
    search_query: str = "",
    sort_mode: str = DEFAULT_SORT_MODE,
) -> HomepageSpotsResult:
    """ホーム画面用にスポット一覧と表示メタ情報を取得する。"""

    normalized_query = (search_query or "").strip()
    normalized_sort = sort_mode if sort_mode in ALLOWED_SORT_MODES else DEFAULT_SORT_MODE

    spots_qs = _base_queryset()
    if normalized_query:
        spots_qs = _apply_search_filter(spots_qs, normalized_query)

    spots_list = list(spots_qs)
    recommendation_source = None
    recommendation_notice = None
    recommendation_scored_ids: List[int] = []

    if normalized_sort == "relevance":
        (
            spots_list,
            recommendation_source,
            recommendation_notice,
            recommendation_scored_ids,
        ) = _apply_recommendation_order(spots_list, user)

    return HomepageSpotsResult(
        spots=spots_list,
        search_query=normalized_query,
        sort_mode=normalized_sort,
        recommendation_source=recommendation_source,
        recommendation_notice=recommendation_notice,
        recommendation_scored_ids=recommendation_scored_ids,
    )


def _base_queryset() -> QuerySet[Spot]:
    return (
        Spot.objects.all()
        .select_related("created_by")
        .prefetch_related("reviews", "tags")
    )


def _apply_search_filter(queryset: QuerySet[Spot], search_query: str) -> QuerySet[Spot]:
    return queryset.filter(
        Q(title__icontains=search_query)
        | Q(description__icontains=search_query)
        | Q(address__icontains=search_query)
        | Q(tags__name__icontains=search_query)
    ).distinct()


def _apply_recommendation_order(
    spots: List[Spot],
    user,
) -> tuple[List[Spot], str | None, str | None, List[int]]:
    if not spots:
        return spots, None, None, []

    if isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return spots, None, "おすすめ順を利用するにはログインしてください。", []

    user_scores = list(
        UserRecommendationScore.objects.filter(user=user, spot__in=spots)
        .select_related("spot")
    )
    if not user_scores:
        return (
            spots,
            None,
            "おすすめスコアがまだ計算されていません。しばらくお待ちください。",
            [],
        )

    score_map = {score.spot_id: score.score for score in user_scores}
    source = user_scores[0].source if user_scores else None

    scored_spots: List[Spot] = []
    unscored_spots: List[Spot] = []

    for spot in spots:
        (scored_spots if spot.id in score_map else unscored_spots).append(spot)

    scored_spots.sort(key=lambda spot: score_map.get(spot.id, 0), reverse=True)
    sorted_spots = scored_spots + unscored_spots
    recommendation_scored_ids = [spot.id for spot in scored_spots]
    notice = _build_recommendation_notice(source)

    return sorted_spots, source, notice, recommendation_scored_ids


def _build_recommendation_notice(source: str | None) -> str:
    if source == "api":
        return "AIが分析したおすすめ順で表示しています。(beta)"
    if source == "fallback":
        return "閲覧履歴をもとに推定したおすすめ順です。"
    return "おすすめ順で表示しています。"
