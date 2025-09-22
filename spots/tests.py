import tempfile
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Spot, Tag
from .services import ExternalSpotService, LocalSpotService, SpotServiceError, get_spot_service


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


class SpotServiceFactoryTests(TestCase):
    def test_get_spot_service_returns_local_by_default(self):
        service = get_spot_service()
        self.assertIsInstance(service, LocalSpotService)

    @override_settings(SPOT_API_CONFIG={'USE_EXTERNAL': True, 'BASE_URL': 'https://api.example.com'})
    def test_get_spot_service_returns_external_when_enabled(self):
        service = get_spot_service()
        self.assertIsInstance(service, ExternalSpotService)


class ExternalSpotServiceTests(TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.response = MagicMock()
        self.response.status_code = 200
        self.session.request.return_value = self.response
        self.service = ExternalSpotService(
            'https://api.example.com',
            session=self.session,
            endpoints={'search': '/search/', 'list': '/spots/', 'create': '/spots/add/'},
        )

    def test_search_spots_calls_external_api(self):
        self.response.json.return_value = {'results': [{'id': 1, 'title': '海'}]}

        results = self.service.search_spots(query='海', request=None)

        self.session.request.assert_called_once_with(
            'GET',
            'https://api.example.com/search/',
            headers={},
            params={'q': '海'},
            timeout=5.0,
        )
        self.assertEqual(results, [{'id': 1, 'title': '海'}])

    def test_search_spots_raises_on_error_status(self):
        self.response.status_code = 500
        self.response.json.return_value = {'error': 'boom'}

        with self.assertRaises(SpotServiceError) as ctx:
            self.service.search_spots(query='海', request=None)

        self.assertEqual(ctx.exception.status_code, 500)

    def test_create_spot_sends_payload_and_returns_spot(self):
        self.response.json.return_value = {'success': True, 'spot': {'id': 99, 'title': '新スポット'}}

        upload = SimpleUploadedFile('sample.jpg', b'data', content_type='image/jpeg')
        request = type('Req', (), {
            'POST': {
                'title': '新スポット',
                'description': '説明',
                'latitude': '35.0',
                'longitude': '139.0',
                'address': '東京',
                'image_url': '',
            },
            'FILES': {'image': upload},
        })()

        spot = self.service.create_spot(request=request)

        self.assertEqual(spot['id'], 99)
        args, kwargs = self.session.request.call_args
        self.assertEqual(args[0], 'POST')
        self.assertEqual(args[1], 'https://api.example.com/spots/add/')
        self.assertIn('files', kwargs)
        self.assertIn('image', kwargs['files'])
        self.assertEqual(kwargs['data']['title'], '新スポット')

    def test_create_spot_raises_when_api_reports_failure(self):
        self.response.json.return_value = {'success': False, 'error': 'invalid'}

        request = type('Req', (), {'POST': {'title': 't', 'description': 'd'}, 'FILES': {}})()

        with self.assertRaises(SpotServiceError) as ctx:
            self.service.create_spot(request=request)

        self.assertEqual(ctx.exception.status_code, 502)


class SpotApiServiceDelegationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='carol', password='carolpass123')

    def test_search_spots_api_uses_service(self):
        fake_service = MagicMock()
        fake_service.search_spots.return_value = [{'id': 1}]
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.get(reverse('search_spots_api'), {'q': '東京'})

        fake_service.search_spots.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'results': [{'id': 1}]})

    def test_search_spots_api_handles_service_error(self):
        fake_service = MagicMock()
        fake_service.search_spots.side_effect = SpotServiceError('NG', status_code=502)
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.get(reverse('search_spots_api'), {'q': '東京'})

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json(), {'results': [], 'error': 'NG'})

    def test_spots_api_uses_service(self):
        fake_service = MagicMock()
        fake_service.list_spots.return_value = [{'id': 1, 'title': '東京'}]
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.get(reverse('spots_api'), {'filter': 'mine'})

        fake_service.list_spots.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'spots': [{'id': 1, 'title': '東京'}]})

    def test_spots_api_handles_service_error(self):
        fake_service = MagicMock()
        fake_service.list_spots.side_effect = SpotServiceError('NG', status_code=503)
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.get(reverse('spots_api'))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {'spots': [], 'error': 'NG'})

    def test_add_spot_api_uses_service(self):
        self.client.force_login(self.user)
        fake_service = MagicMock()
        fake_service.create_spot.return_value = {'id': 10}
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.post(reverse('add_spot_api'), {
                'title': '東京',
                'description': '説明',
                'latitude': '35.0',
                'longitude': '139.0',
            })

        fake_service.create_spot.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True, 'spot': {'id': 10}})

    def test_add_spot_api_handles_service_error(self):
        self.client.force_login(self.user)
        fake_service = MagicMock()
        fake_service.create_spot.side_effect = SpotServiceError('NG', status_code=400)
        with patch('spots.views.get_spot_service', return_value=fake_service):
            response = self.client.post(reverse('add_spot_api'), {
                'title': '東京',
                'description': '説明',
                'latitude': '35.0',
                'longitude': '139.0',
            })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'success': False, 'error': 'NG'})
