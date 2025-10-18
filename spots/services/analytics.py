"""ユーザー閲覧データを活用したレコメンドロジック。"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Set

import requests
from django.conf import settings
from django.utils import timezone

from ..models import UserSpotInteraction

logger = logging.getLogger(__name__)


@dataclass
class RecommendationResult:
    """並び替え結果とメタ情報を保持するデータクラス。"""

    spots: List
    source: str = 'none'  # 'api' | 'fallback' | 'none'
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

    # 全スポット情報をAIに渡して、未閲覧スポットも含めて分析させる
    api_scores = _request_scores_from_openai(user, interactions, all_spots=spots_list)
    scores: Dict[int, float]
    source = 'none'

    if api_scores:
        scores = api_scores
        source = 'api'
    else:
        fallback_scores = {
            interaction.spot_id: _compute_fallback_score(interaction)
            for interaction in interactions
        }
        if any(score > 0 for score in fallback_scores.values()):
            scores = fallback_scores
            source = 'fallback'
        else:
            return RecommendationResult(spots_list)

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
        source=source,
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

    return view_bonus + recency_bonus + duration_bonus


def _request_scores_from_openai(
    user,
    user_interactions: Iterable[UserSpotInteraction],
    all_spots: Sequence = None,
) -> Dict[int, float]:
    """OpenAI API からスコアを取得する。失敗時は空 dict を返す。
    
    Args:
        user: 対象ユーザー
        user_interactions: ユーザーの閲覧履歴
        all_spots: 全スポットのリスト。Noneの場合は閲覧済みスポットのみスコアリング
    """

    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        logger.debug('OPENAI_API_KEY が設定されていないため、API連携をスキップします。')
        return {}

    url = getattr(
        settings,
        'OPENAI_RECOMMENDATION_URL',
        'https://api.openai.com/v1/chat/completions',
    )
    model = getattr(settings, 'OPENAI_RECOMMENDATION_MODEL', 'gpt-4o-mini')
    timeout = getattr(settings, 'OPENAI_TIMEOUT', 15)

    # ユーザーの閲覧履歴
    interaction_payload = [_serialize_interaction(interaction) for interaction in user_interactions]
    
    # スコアリング対象のスポット一覧
    target_spots_payload = []
    if all_spots:
        # 全スポットをスコアリング対象とする
        for spot in all_spots:
            target_spots_payload.append({
                'spot_id': spot.id,
                'title': spot.title,
                'description': spot.description,
                'tags': [tag.name for tag in spot.tags.all()],
            })
    
    system_prompt = (
        'あなたは旅行アプリのレコメンドAIです。ユーザーの閲覧履歴を受け取り、'
        '各スポットの関連度スコア(0〜100)を JSON 形式で返してください。\n\n'
        '重要な指示:\n'
        '1. ユーザーが過去に閲覧したスポット(interactions)の傾向を分析してください。\n'
        '2. 全スポットリスト(target_spots)には、ユーザーがまだ見ていないスポットも含まれています。\n'
        '3. 閲覧済みスポットと類似のタグ、説明、テーマを持つ未閲覧スポットは、高いスコアを付けてください。\n'
        '4. ユーザーの興味・嗜好に合致する新しい発見となるスポットを積極的に推薦してください。\n'
        '5. 出力形式: {"scores": [{"spot_id": number, "score": number, "reason": string}]}\n'
        '   reasonには推薦理由を簡潔に記述してください(任意)。'
    )

    user_message_content = {
        'user': user.username,
        'interactions': interaction_payload,
    }
    if target_spots_payload:
        user_message_content['target_spots'] = target_spots_payload

    messages = [
        {"role": 'system', "content": system_prompt},
        {
            "role": 'user',
            "content": json.dumps(user_message_content, ensure_ascii=False),
        },
    ]

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    payload = {
        'model': model,
        'messages': messages,
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
    except Exception as exc:  # pragma: no cover - ネットワーク例外はログのみ
        logger.warning('OpenAI API の呼び出しに失敗しました: %s', exc)
        return {}

    try:
        response_data = response.json()
    except ValueError:  # pragma: no cover - 想定外のレスポンス
        logger.warning('OpenAI API のレスポンスが JSON ではありません。')
        return {}

    try:
        message_content = response_data['choices'][0]['message']['content']
    except (KeyError, IndexError, TypeError):
        logger.warning('OpenAI API のレスポンス形式が想定外です: %s', response_data)
        return {}

    try:
        parsed = json.loads(message_content)
    except json.JSONDecodeError:
        logger.warning('OpenAI API の応答が JSON 文字列ではありません: %s', message_content)
        return {}

    scores: Dict[int, float] = {}
    reasons: Dict[int, str] = {}
    for item in parsed.get('scores', []):
        try:
            spot_id = int(item['spot_id'])
            score = float(item['score'])
        except (KeyError, TypeError, ValueError):
            continue
        scores[spot_id] = score
        if 'reason' in item and isinstance(item['reason'], str):
            reasons[spot_id] = item['reason']

    # reasonsも保存できるようにするため、追加情報として返す
    # (既存の戻り値との互換性のため、scoresのみ返すが、必要に応じて拡張可能)
    return scores


def _serialize_interaction(interaction: UserSpotInteraction) -> Dict:
    spot = interaction.spot
    return {
        'spot_id': spot.id,
        'title': spot.title,
        'description': spot.description,
        'tags': [tag.name for tag in spot.tags.all()],
        'view_count': interaction.view_count,
        'total_view_seconds': interaction.total_view_duration.total_seconds(),
        'last_viewed_at': interaction.last_viewed_at.isoformat(),
    }

