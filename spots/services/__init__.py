"""サービス層のユーティリティをまとめるパッケージ。"""

from .analytics import RecommendationResult, order_spots_by_relevance
from .recommendation_jobs import (
    RecommendationToolCall,
    build_recommendation_tool_context,
    build_recommendation_tool_schema,
    build_tool_call_from_result,
    compute_and_store_all_user_scores,
    get_or_create_job_setting,
    is_job_due,
    run_recommendation_for_user,
    store_recommendation_scores,
    update_last_run,
)

__all__ = [
    'RecommendationResult',
    'RecommendationToolCall',
    'build_recommendation_tool_context',
    'build_recommendation_tool_schema',
    'build_tool_call_from_result',
    'compute_and_store_all_user_scores',
    'get_or_create_job_setting',
    'is_job_due',
    'order_spots_by_relevance',
    'run_recommendation_for_user',
    'store_recommendation_scores',
    'update_last_run',
]
