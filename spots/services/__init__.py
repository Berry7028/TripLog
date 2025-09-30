"""サービス層のユーティリティをまとめるパッケージ。"""

from .analytics import RecommendationResult, order_spots_by_relevance

__all__ = ['RecommendationResult', 'order_spots_by_relevance']
