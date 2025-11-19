from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from spots.models import Spot
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

    def _create_spot(self, title: str) -> Spot:
        return Spot.objects.create(
            title=title,
            description="sample",
            latitude=35.0,
            longitude=139.0,
            address="Tokyo",
            created_by=self.owner,
        )
