import tempfile
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import quote_plus

from django.contrib.auth.models import Group, Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .forms import SpotForm
from .image_providers import get_spot_fallback_image
from .models import Review, Spot, SpotView, Tag, UserProfile, UserSpotInteraction
from .services import order_spots_by_relevance


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
        with patch('spots.image_providers.get_spot_fallback_image', return_value=None) as mocked:
            spot = self.create_spot()
            self.assertEqual(spot.image_src, '')
            mocked.assert_called_once_with(spot.title)

    def test_image_src_uses_unsplash_fallback(self):
        fallback_url = 'https://images.unsplash.com/photo-123456'
        with patch('spots.image_providers.get_spot_fallback_image', return_value=fallback_url) as mocked:
            spot = self.create_spot()
            self.assertEqual(spot.image_src, fallback_url)
            mocked.assert_called_once_with(spot.title)


class SpotImageProviderTests(TestCase):
    def test_fallback_uses_source_url_without_api_key(self):
        with override_settings(UNSPLASH_ACCESS_KEY=None, UNSPLASH_DEFAULT_ORIENTATION='landscape'):
            url = get_spot_fallback_image('渋谷 スカイ')

        self.assertTrue(url.startswith('https://source.unsplash.com/featured/'))
        self.assertIn(quote_plus('渋谷 スカイ'), url)
        self.assertIn('orientation=landscape', url)

    def test_fallback_returns_none_when_no_query_available(self):
        with override_settings(UNSPLASH_ACCESS_KEY=None, UNSPLASH_FALLBACK_QUERY=''):
            self.assertIsNone(get_spot_fallback_image(''))


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
        self.assertTrue(spot_payload['image'])
        self.assertTrue(spot_payload['image'].startswith('https://'))
        self.assertEqual(spot_payload['tags'], [self.tag_other.name])

    def test_spots_api_ignores_filter_when_anonymous(self):
        response = self.client.get(reverse('spots_api'), {'filter': 'mine'})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        returned_ids = {spot['id'] for spot in data['spots']}
        self.assertSetEqual(returned_ids, {self.owned_spot.id, self.other_spot.id})


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='staffpass123', is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='visitor', password='visitorpass123'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_dashboard_denies_non_staff(self):
        self.client.force_login(self.normal_user)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))

    def test_dashboard_renders_for_staff(self):
        tag = Tag.objects.create(name='絶景')
        spot = Spot.objects.create(
            title='展望台',
            description='夜景がきれい',
            latitude=35.0,
            longitude=135.0,
            address='大阪府',
            created_by=self.staff,
            is_ai_generated=True,
        )
        spot.tags.add(tag)
        Review.objects.create(spot=spot, user=self.staff, rating=5, comment='最高！')
        SpotView.objects.create(spot=spot)

        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ダッシュボード')
        self.assertContains(response, '展望台')


class SpotFormAdminBehaviorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='creator', password='creatorpass123')

    def test_spot_form_saves_tags_and_creator(self):
        form = SpotForm(
            data={
                'title': '灯台',
                'description': '海沿いの灯台',
                'latitude': 33.0,
                'longitude': 132.0,
                'address': '愛媛県',
                'image_url': '',
                'tags_text': '海, 灯台, 海',
            }
        )
        self.assertTrue(form.is_valid())
        spot = form.save(user=self.user)
        self.assertEqual(spot.created_by, self.user)
        self.assertEqual(sorted(spot.tags.values_list('name', flat=True)), ['海', '灯台'])


class AdminSpotCrudTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staffer', password='staffpass123', is_staff=True
        )
        self.other_user = User.objects.create_user(username='other', password='otherpass123')

    def test_staff_can_create_spot_via_admin(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_spot_add'),
            data={
                'title': '山頂カフェ',
                'description': '絶景カフェ',
                'latitude': '36.5',
                'longitude': '137.8',
                'address': '長野県大町市',
                'image_url': '',
                'created_by': self.other_user.id,
                'is_ai_generated': 'on',
                'tags_text': 'カフェ, 山',
            },
        )
        self.assertEqual(response.status_code, 302)
        spot = Spot.objects.get(title='山頂カフェ')
        self.assertEqual(spot.created_by, self.other_user)
        self.assertTrue(spot.is_ai_generated)
        self.assertSetEqual(set(spot.tags.values_list('name', flat=True)), {'カフェ', '山'})

    def test_non_staff_cannot_access_spot_admin(self):
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('admin_spot_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))


class AdminUserUpdateTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staffuser', password='staffpass123', is_staff=True
        )
        perms = Permission.objects.filter(codename__in=['view_user', 'change_user'])
        self.staff.user_permissions.add(*perms)
        self.target = User.objects.create_user(
            username='target', password='targetpass123', email='old@example.com'
        )
        self.spot = Spot.objects.create(
            title='公園',
            description='大きな公園',
            latitude=34.7,
            longitude=135.5,
            address='兵庫県',
            created_by=self.staff,
        )

    def test_staff_can_update_user_profile(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_user_detail', args=[self.target.id]),
            data={
                'username': 'target',
                'email': 'new@example.com',
                'is_active': 'on',
                'bio': '旅好き',
                'favorite_spots': [str(self.spot.id)],
            },
        )
        self.assertEqual(response.status_code, 302)
        target = User.objects.get(pk=self.target.pk)
        self.assertEqual(target.email, 'new@example.com')
        self.assertFalse(target.is_staff)
        profile = UserProfile.objects.get(user=target)
        self.assertEqual(profile.bio, '旅好き')
        self.assertSetEqual(set(profile.favorite_spots.values_list('id', flat=True)), {self.spot.id})


class AdminReviewCreateTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staff', password='staffpass123', is_staff=True
        )
        self.spot_owner = User.objects.create_user(username='author', password='authorpass123')
        self.reviewer = User.objects.create_user(username='critic', password='criticpass123')
        self.spot = Spot.objects.create(
            title='滝',
            description='美しい滝',
            latitude=35.2,
            longitude=136.1,
            address='岐阜県',
            created_by=self.spot_owner,
        )

    def test_staff_can_create_review_via_admin(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_review_add'),
            data={
                'spot': self.spot.id,
                'user': self.reviewer.id,
                'rating': 4,
                'comment': '雰囲気が最高',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(spot=self.spot, user=self.reviewer, rating=4).exists())

    def test_bulk_delete_reviews(self):
        review1 = Review.objects.create(spot=self.spot, user=self.reviewer, rating=5, comment='good')
        review2 = Review.objects.create(spot=self.spot, user=self.staff, rating=3, comment='ok')
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_review_list'),
            data={
                'action': 'delete_selected',
                'selected': [str(review1.id), str(review2.id)],
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id__in=[review1.id, review2.id]).exists())


class AdminUserCreationTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='adminstaff', password='staffpass123', is_staff=True
        )
        perms = Permission.objects.filter(codename__in=['view_user', 'add_user'])
        self.staff.user_permissions.add(*perms)
        self.group = Group.objects.create(name='Editors')
        self.permission = Permission.objects.first()

    def test_staff_creates_user_without_privileged_fields(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_user_add'),
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'Securepass123',
                'password2': 'Securepass123',
                'is_active': 'on',
            },
        )
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username='newuser')
        self.assertFalse(created.is_staff)
        self.assertFalse(created.groups.exists())
        self.assertFalse(created.user_permissions.exists())


class AdminUserPasswordChangeTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='superstaff', password='staffpass123', is_staff=True
        )
        perms = Permission.objects.filter(codename__in=['view_user', 'change_user'])
        self.staff.user_permissions.add(*perms)
        self.target = User.objects.create_user(username='member', password='oldpass123')

    def test_staff_can_change_password(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_user_password', args=[self.target.id]),
            data={'password1': 'Newpass123', 'password2': 'Newpass123'},
        )
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        login_success = self.client.login(username='member', password='Newpass123')
        self.assertTrue(login_success)


class AdminGroupCrudTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='groupstaff', password='staffpass123', is_staff=True
        )
        self.permission = Permission.objects.filter(content_type__app_label='auth').first()

    def test_staff_can_create_and_delete_group(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_group_add'),
            data={
                'name': 'Moderators',
                'permissions': [str(self.permission.id)] if self.permission else [],
            },
        )
        self.assertEqual(response.status_code, 302)
        group = Group.objects.get(name='Moderators')
        if self.permission:
            self.assertIn(self.permission, group.permissions.all())

        response = self.client.post(reverse('admin_group_delete', args=[group.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Group.objects.filter(name='Moderators').exists())


class AdminProfileAndLogListTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='profilestaff', password='staffpass123', is_staff=True
        )
        self.user = User.objects.create_user(username='profile_user', password='pass12345')
        self.spot = Spot.objects.create(
            title='灯台',
            description='海沿いの灯台',
            latitude=33.0,
            longitude=132.0,
            address='愛媛県',
            created_by=self.staff,
        )
        self.profile = UserProfile.objects.create(user=self.user, bio='旅好き')
        self.profile.favorite_spots.add(self.spot)
        SpotView.objects.create(spot=self.spot)

    def test_profile_list_accessible(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_profile_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '旅好き')

    def test_spotview_list_filter(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_spotview_list'), {'spot': self.spot.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.spot.title)


class UserSpotInteractionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewer', password='viewpass123')
        self.spot = Spot.objects.create(
            title='展望台',
            description='夜景がきれい',
            latitude=35.0,
            longitude=135.0,
            address='大阪府',
            created_by=self.user,
        )

    def test_detail_view_creates_interaction_and_counts_click(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('spot_detail', args=[self.spot.id]))
        self.assertEqual(response.status_code, 200)

        interaction = UserSpotInteraction.objects.get(user=self.user, spot=self.spot)
        self.assertEqual(interaction.view_count, 1)
        self.assertEqual(interaction.total_view_duration.total_seconds(), 0)

    def test_multiple_visits_increment_view_count(self):
        self.client.force_login(self.user)
        self.client.get(reverse('spot_detail', args=[self.spot.id]))
        self.client.get(reverse('spot_detail', args=[self.spot.id]))

        interaction = UserSpotInteraction.objects.get(user=self.user, spot=self.spot)
        self.assertEqual(interaction.view_count, 2)

    def test_record_spot_view_updates_duration(self):
        self.client.force_login(self.user)
        self.client.get(reverse('spot_detail', args=[self.spot.id]))

        response = self.client.post(
            reverse('record_spot_view', args=[self.spot.id]),
            data={'duration_ms': '1500'},
        )
        self.assertEqual(response.status_code, 200)

        interaction = UserSpotInteraction.objects.get(user=self.user, spot=self.spot)
        self.assertEqual(interaction.view_count, 1)
        self.assertAlmostEqual(
            interaction.total_view_duration.total_seconds(),
            1.5,
            places=1,
        )

    def test_record_spot_view_requires_login(self):
        response = self.client.post(
            reverse('record_spot_view', args=[self.spot.id]),
            data={'duration_ms': '1000'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)


class RecommendationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reco', password='recopass123')
        self.other = User.objects.create_user(username='other', password='otherpass123')

        self.spot1 = Spot.objects.create(
            title='港',
            description='夕焼けが綺麗な港',
            latitude=34.0,
            longitude=135.0,
            address='兵庫県',
            created_by=self.other,
        )
        self.spot2 = Spot.objects.create(
            title='山頂',
            description='登山コースの絶景',
            latitude=36.0,
            longitude=138.0,
            address='長野県',
            created_by=self.other,
        )
        self.spot3 = Spot.objects.create(
            title='美術館',
            description='現代アートが豊富',
            latitude=35.6,
            longitude=139.7,
            address='東京都',
            created_by=self.other,
        )

        now = timezone.now()
        i1 = UserSpotInteraction.objects.create(
            user=self.user,
            spot=self.spot1,
            view_count=3,
            total_view_duration=timedelta(minutes=5),
        )
        i2 = UserSpotInteraction.objects.create(
            user=self.user,
            spot=self.spot2,
            view_count=2,
            total_view_duration=timedelta(minutes=8),
        )
        i3 = UserSpotInteraction.objects.create(
            user=self.user,
            spot=self.spot3,
            view_count=1,
            total_view_duration=timedelta(seconds=45),
        )

        UserSpotInteraction.objects.filter(pk=i1.pk).update(last_viewed_at=now - timedelta(hours=1))
        UserSpotInteraction.objects.filter(pk=i2.pk).update(last_viewed_at=now - timedelta(days=2))
        UserSpotInteraction.objects.filter(pk=i3.pk).update(last_viewed_at=now - timedelta(days=10))

    def test_order_spots_by_relevance_without_history(self):
        result = order_spots_by_relevance([self.spot1, self.spot2], self.other)
        self.assertEqual(result.source, 'none')
        self.assertEqual([spot.id for spot in result.spots], [self.spot1.id, self.spot2.id])

    def test_order_spots_by_relevance_fallback(self):
        result = order_spots_by_relevance([self.spot1, self.spot2, self.spot3], self.user)
        self.assertEqual(result.source, 'fallback')
        ordered_ids = [spot.id for spot in result.spots]
        self.assertEqual(ordered_ids[0], self.spot1.id)
        self.assertIn(self.spot2.id, ordered_ids[1:])
        self.assertEqual(result.scored_spot_ids, {self.spot1.id, self.spot2.id, self.spot3.id})

    def test_order_spots_by_relevance_uses_api_scores_when_available(self):
        with patch('spots.services.analytics._request_scores_from_openrouter') as mock_request:
            mock_request.return_value = {
                self.spot2.id: 92.0,
                self.spot1.id: 75.0,
            }
            result = order_spots_by_relevance([self.spot1, self.spot2, self.spot3], self.user)

        self.assertEqual(result.source, 'api')
        ordered_ids = [spot.id for spot in result.spots]
        self.assertEqual(ordered_ids[0], self.spot2.id)
        self.assertEqual(ordered_ids[1], self.spot1.id)
