from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from spots.models import Spot, UserRecommendationScore
from spots.services.homepage import fetch_homepage_spots


class FetchHomepageSpotsTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="pass1234",
        )
        self.owner = get_user_model().objects.create_user(
            username="owner",
            password="pass1234",
        )

    def test_invalid_sort_mode_defaults_to_recent_and_trims_query(self):
        spot = self._create_spot("Beach Escape")

        result = fetch_homepage_spots(
            user=AnonymousUser(),
            search_query="  Beach  ",
            sort_mode="unknown",
        )

        self.assertEqual(result.sort_mode, "recent")
        self.assertEqual(result.search_query, "Beach")
        self.assertIn(spot, result.spots)

    def test_relevance_sort_uses_scores_and_sets_notice(self):
        spot_a = self._create_spot("Mountain View")
        spot_b = self._create_spot("City Lights")
        spot_c = self._create_spot("Ocean Breeze")

        UserRecommendationScore.objects.create(
            user=self.user,
            spot=spot_b,
            score=75.0,
            source="api",
        )
        UserRecommendationScore.objects.create(
            user=self.user,
            spot=spot_a,
            score=90.0,
            source="api",
        )

        result = fetch_homepage_spots(
            user=self.user,
            search_query="",
            sort_mode="relevance",
        )

        self.assertEqual(result.sort_mode, "relevance")
        self.assertEqual(result.recommendation_source, "api")
        self.assertEqual(
            result.recommendation_notice,
            "AIが分析したおすすめ順で表示しています。(beta)",
        )
        self.assertEqual(result.recommendation_scored_ids, [spot_a.id, spot_b.id])
        self.assertEqual([spot.id for spot in result.spots[:3]], [spot_a.id, spot_b.id, spot_c.id])

    def test_relevance_sort_requires_login(self):
        self._create_spot("Hidden Gem")

        result = fetch_homepage_spots(
            user=AnonymousUser(),
            search_query="",
            sort_mode="relevance",
        )

        self.assertEqual(
            result.recommendation_notice,
            "おすすめ順を利用するにはログインしてください。",
        )
        self.assertEqual(result.recommendation_scored_ids, [])
        self.assertIsNone(result.recommendation_source)

    def _create_spot(self, title: str) -> Spot:
        return Spot.objects.create(
            title=title,
            description="sample",
            latitude=35.0,
            longitude=139.0,
            address="Tokyo",
            created_by=self.owner,
        )
