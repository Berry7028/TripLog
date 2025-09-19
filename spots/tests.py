from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

import tempfile

from .models import Spot, Tag


class SpotImageSrcTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='testpass123')

    def create_spot(self, **kwargs):
        defaults = {
            'title': 'テストスポット',
            'description': '説明',
            'latitude': 35.0,
            'longitude': 139.0,
            'address': '東京都',
            'created_by': self.user,
        }
        defaults.update(kwargs)
        return Spot.objects.create(**defaults)

    def test_image_src_prefers_uploaded_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.settings(MEDIA_ROOT=tmpdir):
                uploaded_file = SimpleUploadedFile('sample.jpg', b'filecontent', content_type='image/jpeg')
                spot = self.create_spot(image=uploaded_file, image_url='https://example.com/fallback.jpg')
                self.assertEqual(spot.image_src, spot.image.url)

    def test_image_src_returns_image_url_when_available(self):
        spot = self.create_spot(image_url='https://example.com/external.jpg')
        self.assertEqual(spot.image_src, 'https://example.com/external.jpg')

    def test_image_src_returns_empty_string_when_no_image(self):
        spot = self.create_spot()
        self.assertEqual(spot.image_src, '')


class SpotsApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='alice', password='alicepass123')
        cls.other_user = User.objects.create_user(username='bob', password='bobpass123')

        cls.tag_owned = Tag.objects.create(name='海')
        cls.tag_other = Tag.objects.create(name='山')

        cls.owned_spot = Spot.objects.create(
            title='ビーチ',
            description='美しい海',
            latitude=34.0,
            longitude=135.0,
            address='沖縄県',
            created_by=cls.owner,
            image_url='https://example.com/beach.jpg',
        )
        cls.owned_spot.tags.add(cls.tag_owned)

        cls.other_spot = Spot.objects.create(
            title='山頂',
            description='登山ルート',
            latitude=36.0,
            longitude=138.0,
            address='長野県',
            created_by=cls.other_user,
        )
        cls.other_spot.tags.add(cls.tag_other)

    def test_spots_api_returns_only_mine_for_authenticated_user(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('spots_api'), {'filter': 'mine'})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data['spots']), 1)
        spot_payload = data['spots'][0]
        self.assertEqual(spot_payload['id'], self.owned_spot.id)
        self.assertEqual(spot_payload['created_by'], self.owner.username)
        self.assertEqual(spot_payload['image'], self.owned_spot.image_url)
        self.assertEqual(spot_payload['tags'], [self.tag_owned.name])

    def test_spots_api_returns_only_others_for_authenticated_user(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('spots_api'), {'filter': 'others'})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data['spots']), 1)
        spot_payload = data['spots'][0]
        self.assertEqual(spot_payload['id'], self.other_spot.id)
        self.assertEqual(spot_payload['created_by'], self.other_user.username)
        self.assertIsNone(spot_payload['image'])
        self.assertEqual(spot_payload['tags'], [self.tag_other.name])

    def test_spots_api_ignores_filter_when_anonymous(self):
        response = self.client.get(reverse('spots_api'), {'filter': 'mine'})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        returned_ids = {spot['id'] for spot in data['spots']}
        self.assertSetEqual(returned_ids, {self.owned_spot.id, self.other_spot.id})
