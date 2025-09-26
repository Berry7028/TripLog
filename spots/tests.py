from django.contrib.auth.models import Group, Permission, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

import tempfile

from .forms import SpotForm
from .models import Review, Spot, SpotView, Tag, UserProfile


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
                'is_staff': 'on',
                'bio': '旅好き',
                'favorite_spots': [str(self.spot.id)],
            },
        )
        self.assertEqual(response.status_code, 302)
        target = User.objects.get(pk=self.target.pk)
        self.assertEqual(target.email, 'new@example.com')
        self.assertTrue(target.is_staff)
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
        self.group = Group.objects.create(name='Editors')
        self.permission = Permission.objects.first()

    def test_staff_can_create_user_with_group(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse('admin_user_add'),
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'Securepass123',
                'password2': 'Securepass123',
                'is_active': 'on',
                'is_staff': 'on',
                'groups': [str(self.group.id)],
                'user_permissions': [str(self.permission.id)] if self.permission else [],
            },
        )
        self.assertEqual(response.status_code, 302)
        created = User.objects.get(username='newuser')
        self.assertTrue(created.is_staff)
        self.assertIn(self.group, created.groups.all())
        if self.permission:
            self.assertIn(self.permission, created.user_permissions.all())


class AdminUserPasswordChangeTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='superstaff', password='staffpass123', is_staff=True
        )
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
