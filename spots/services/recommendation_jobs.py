"""AIおすすめ解析ジョブとツールコール連携のユーティリティ。"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from ..models import (
    RecommendationJobLog,
    RecommendationJobSetting,
    Spot,
    UserRecommendationScore,
    UserSpotInteraction,
)
from .analytics import RecommendationResult, order_spots_by_relevance

logger = logging.getLogger(__name__)

TOOL_NAME = 'store_user_recommendation_scores'
TOOL_SCHEMA_VERSION = '1.0'
DEFAULT_INTERVAL_HOURS = 1  # 1時間に1回実行


@dataclass(frozen=True)
class RecommendationToolCall:
    """AI がスコア計算後に呼び出すツールコール定義。"""

    name: str
    arguments: Dict[str, Any]
    schema_version: str = TOOL_SCHEMA_VERSION

    def to_openai_tool_call(self) -> Dict[str, Any]:
        """OpenAI 互換 API で利用できるツールコール形式に変換する。"""

        return {
            'type': 'function',
            'function': {
                'name': self.name,
                'arguments': json.dumps(self.arguments, ensure_ascii=False),
            },
        }


def get_or_create_job_setting() -> RecommendationJobSetting:
    """シングルトン設定を取得または作成する。"""

    setting = RecommendationJobSetting.objects.order_by('id').first()
    if setting:
        return setting
    return RecommendationJobSetting.objects.create(interval_hours=DEFAULT_INTERVAL_HOURS)


def is_job_due(setting: RecommendationJobSetting, now=None) -> bool:
    """設定に基づき次のジョブ実行が必要か判定する。"""

    if not setting.enabled:
        return False
    if setting.last_run_at is None:
        return True
    if now is None:
        now = timezone.now()
    elapsed = now - setting.last_run_at
    return elapsed.total_seconds() >= setting.interval_hours * 3600


def update_last_run(setting: RecommendationJobSetting, now=None) -> None:
    """最終実行日時を更新する。"""

    if now is None:
        now = timezone.now()
    setting.last_run_at = now
    setting.save(update_fields=['last_run_at', 'updated_at'])


def build_recommendation_tool_schema() -> List[Dict[str, Any]]:
    """LLM に公開するツールのスキーマを返す。"""

    return [
        {
            'type': 'function',
            'function': {
                'name': TOOL_NAME,
                'description': (
                    'ユーザーごとのおすすめスコアを保存します。'
                    'scores 配列には {"spot_id": number, "score": number, "reason": string?} の形で渡してください。'
                    'user_id または username を必ず含め、score は 0-100 の範囲を推奨します。'
                ),
                'parameters': {
                    'type': 'object',
                    'properties': {
                        'user_id': {
                            'type': 'integer',
                            'description': 'スコア対象ユーザーのID。指定が無い場合 username を利用します。',
                        },
                        'username': {
                            'type': 'string',
                            'description': 'スコア対象ユーザーのユーザー名。',
                        },
                        'schema_version': {
                            'type': 'string',
                            'description': 'ツールコールのバージョン。現在は 1.0 を使用します。',
                            'enum': [TOOL_SCHEMA_VERSION],
                        },
                        'source': {
                            'type': 'string',
                            'description': 'スコア算出元 (api / fallback / manual など)。',
                        },
                        'scores': {
                            'type': 'array',
                            'description': 'スポットごとのスコア一覧。',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'spot_id': {'type': 'integer'},
                                    'score': {'type': 'number'},
                                    'reason': {
                                        'type': 'string',
                                        'description': '任意の補足説明。',
                                    },
                                },
                                'required': ['spot_id', 'score'],
                                'additionalProperties': False,
                            },
                        },
                        'notes': {
                            'type': 'string',
                            'description': '解析メモや備考。',
                        },
                    },
                    'required': ['scores'],
                    'additionalProperties': False,
                },
            },
        }
    ]


def build_recommendation_tool_context(
    user,
    interactions: Iterable[UserSpotInteraction],
) -> Dict[str, Any]:
    """LLM に渡すコンテキスト情報を構築する。"""

    payload = {
        'schema_version': TOOL_SCHEMA_VERSION,
        'user': {
            'id': user.id,
            'username': user.username,
        },
        'interactions': [],
    }
    for interaction in interactions:
        spot = interaction.spot
        payload['interactions'].append(
            {
                'spot_id': spot.id,
                'title': spot.title,
                'description': spot.description,
                'tags': [tag.name for tag in spot.tags.all()],
                'view_count': interaction.view_count,
                'total_view_seconds': interaction.total_view_duration.total_seconds(),
                'last_viewed_at': interaction.last_viewed_at.isoformat(),
            }
        )
    return payload


def build_tool_call_from_result(user, result: RecommendationResult) -> RecommendationToolCall:
    """解析結果からツールコールのペイロードを組み立てる。"""

    scores = []
    for spot_id in sorted(result.scored_spot_ids):
        scores.append(
            {
                'spot_id': spot_id,
                'score': float(result.scores.get(spot_id, 0.0)),
            }
        )
    arguments = {
        'user_id': user.id,
        'username': user.username,
        'schema_version': TOOL_SCHEMA_VERSION,
        'source': result.source,
        'scores': scores,
    }
    return RecommendationToolCall(name=TOOL_NAME, arguments=arguments)


def store_recommendation_scores(
    arguments: Dict[str, Any],
    *,
    triggered_by: str = RecommendationJobLog.TRIGGER_API,
    metadata: Optional[Dict[str, Any]] = None,
) -> RecommendationJobLog:
    """AI からのツールコール内容を保存する。"""

    user = _resolve_user(arguments)
    if user is None:
        raise ValueError('ユーザー情報 (user_id または username) を特定できません。')

    raw_scores = arguments.get('scores') or []
    if not isinstance(raw_scores, list):
        raise ValueError('scores は配列である必要があります。')

    cleaned_scores: List[Dict[str, Any]] = []
    scored_ids: List[int] = []
    for item in raw_scores:
        if not isinstance(item, dict):
            continue
        try:
            spot_id = int(item['spot_id'])
            score = float(item['score'])
        except (KeyError, TypeError, ValueError):
            continue
        cleaned = {'spot_id': spot_id, 'score': score}
        if 'reason' in item and isinstance(item['reason'], str):
            cleaned['reason'] = item['reason']
        cleaned_scores.append(cleaned)
        scored_ids.append(spot_id)

    metadata_payload = metadata.copy() if metadata else {}
    metadata_payload.update(
        {
            'tool_payload': {
                'schema_version': arguments.get('schema_version', TOOL_SCHEMA_VERSION),
                'scores': cleaned_scores,
                'notes': arguments.get('notes'),
            }
        }
    )

    log = RecommendationJobLog.objects.create(
        user=user,
        source=(arguments.get('source') or RecommendationJobLog.SOURCE_API),
        triggered_by=triggered_by,
        scored_spot_ids=scored_ids,
        metadata=metadata_payload,
    )
    return log


def run_recommendation_for_user(
    user,
    *,
    triggered_by: str = RecommendationJobLog.TRIGGER_AUTO,
    persist_log: bool = True,
) -> Optional[RecommendationResult]:
    """指定ユーザーの閲覧履歴を解析し、結果を保存する。"""

    interactions = list(
        UserSpotInteraction.objects.filter(user=user)
        .select_related('spot')
        .prefetch_related('spot__tags')
    )
    if not interactions:
        return None

    spots = [interaction.spot for interaction in interactions]
    result = order_spots_by_relevance(spots, user)
    tool_context = build_recommendation_tool_context(user, interactions)

    if persist_log:
        tool_call = build_tool_call_from_result(user, result)
        metadata = {
            'interaction_count': len(interactions),
            'tool_context': tool_context,
        }
        store_recommendation_scores(
            tool_call.arguments,
            triggered_by=triggered_by,
            metadata=metadata,
        )

    return result


def _resolve_user(arguments: Dict[str, Any]):
    """ツールコールで渡されたユーザー情報から User を取得する。"""

    User = get_user_model()
    user = None
    user_id = arguments.get('user_id')
    username = arguments.get('username')

    if user_id is not None:
        try:
            user = User.objects.filter(id=int(user_id)).first()
        except (TypeError, ValueError):
            user = None

    if user is None and username:
        user = User.objects.filter(username=username).first()

    return user


def compute_and_store_all_user_scores(
    *,
    triggered_by: str = RecommendationJobLog.TRIGGER_AUTO,
    batch_size: int = 100,
) -> Dict[str, Any]:
    """全ユーザーのおすすめスコアをバックグラウンドで計算してDBに保存する。
    
    Returns:
        実行結果のサマリー情報
    """
    User = get_user_model()
    
    # 閲覧履歴があるユーザーのみ対象
    users_with_interactions = User.objects.filter(
        spot_interactions__isnull=False
    ).distinct()
    
    # 全スポットを取得(prefetchでタグも取得)
    all_spots = list(
        Spot.objects.all()
        .prefetch_related('tags')
        .order_by('id')
    )
    
    if not all_spots:
        logger.info('スポットが存在しないため、スコア計算をスキップします。')
        return {
            'success': True,
            'users_processed': 0,
            'scores_saved': 0,
            'message': 'スポットが存在しません',
        }
    
    total_users = 0
    total_scores_saved = 0
    errors = []
    
    for user in users_with_interactions:
        try:
            result = _compute_and_store_user_scores(
                user=user,
                all_spots=all_spots,
                triggered_by=triggered_by,
            )
            if result:
                total_users += 1
                total_scores_saved += result.get('scores_saved', 0)
                logger.info(
                    f'ユーザー {user.username} のスコア計算完了: {result.get("scores_saved", 0)}件'
                )
        except Exception as e:
            error_msg = f'ユーザー {user.username} のスコア計算でエラー: {e}'
            logger.error(error_msg)
            errors.append(error_msg)
    
    return {
        'success': len(errors) == 0,
        'users_processed': total_users,
        'scores_saved': total_scores_saved,
        'errors': errors,
        'timestamp': timezone.now().isoformat(),
    }


def _compute_and_store_user_scores(
    user,
    all_spots: List[Spot],
    *,
    triggered_by: str = RecommendationJobLog.TRIGGER_AUTO,
) -> Optional[Dict[str, Any]]:
    """指定ユーザーの全スポットに対するスコアを計算してDBに保存する。"""
    
    # ユーザーの閲覧履歴を取得
    interactions = list(
        UserSpotInteraction.objects.filter(user=user)
        .select_related('spot')
        .prefetch_related('spot__tags')
    )
    
    if not interactions:
        return None
    
    # 全スポットをスコアリング
    result = order_spots_by_relevance(all_spots, user)
    
    if not result.scores:
        logger.warning(f'ユーザー {user.username} のスコア計算結果が空です')
        return None
    
    # トランザクション内でスコアを保存
    with transaction.atomic():
        # 既存のスコアを削除
        UserRecommendationScore.objects.filter(user=user).delete()
        
        # 新しいスコアを一括作成
        scores_to_create = []
        for spot_id, score_value in result.scores.items():
            # spot_idからSpotオブジェクトを取得
            spot = next((s for s in all_spots if s.id == spot_id), None)
            if spot:
                scores_to_create.append(
                    UserRecommendationScore(
                        user=user,
                        spot=spot,
                        score=score_value,
                        source=result.source,
                    )
                )
        
        if scores_to_create:
            UserRecommendationScore.objects.bulk_create(scores_to_create)
        
        # ログを記録
        RecommendationJobLog.objects.create(
            user=user,
            source=result.source,
            triggered_by=triggered_by,
            scored_spot_ids=list(result.scored_spot_ids),
            metadata={
                'interaction_count': len(interactions),
                'total_spots': len(all_spots),
                'scored_count': len(result.scores),
            },
        )
    
    return {
        'scores_saved': len(scores_to_create),
        'source': result.source,
    }
