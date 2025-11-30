from django.urls import path

from . import views, admin_views

urlpatterns = [
    # ホーム・ランキング・ユーザー関連
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('ranking/', views.ranking, name='ranking'),
    path('licenses/', views.licenses, name='licenses'),
    path('my-spots/', views.my_spots, name='my_spots'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),

    # スポット詳細・操作
    path('spot/<int:spot_id>/', views.spot_detail, name='spot_detail'),
    path('spot/<int:spot_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('spot/<int:spot_id>/review/', views.add_review, name='add_review'),
    path('spot/<int:spot_id>/record-view/', views.record_spot_view, name='record_spot_view'),
    path('add/', views.add_spot, name='add_spot'),

    # APIエンドポイント
    path('api/search/', views.search_spots_api, name='search_spots_api'),
    path('api/spots/', views.spots_api, name='spots_api'),
    path('api/spots/add/', views.add_spot_api, name='add_spot_api'),

    # 地図・プラン
    path('map/', views.map_view, name='map'),
    path('plan/', views.plan_view, name='plan'),

    # 管理ダッシュボード
    path('manage/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('manage/spots/', admin_views.SpotAdminListView.as_view(), name='admin_spot_list'),
    path('manage/spots/add/', admin_views.SpotAdminCreateView.as_view(), name='admin_spot_add'),
    path('manage/spots/<int:pk>/edit/', admin_views.SpotAdminUpdateView.as_view(), name='admin_spot_edit'),
    path('manage/spots/<int:pk>/delete/', admin_views.SpotAdminDeleteView.as_view(), name='admin_spot_delete'),
    path('manage/tags/', admin_views.TagAdminListView.as_view(), name='admin_tag_list'),
    path('manage/tags/add/', admin_views.TagAdminCreateView.as_view(), name='admin_tag_add'),
    path('manage/tags/<int:pk>/edit/', admin_views.TagAdminUpdateView.as_view(), name='admin_tag_edit'),
    path('manage/tags/<int:pk>/delete/', admin_views.TagAdminDeleteView.as_view(), name='admin_tag_delete'),
    path('manage/reviews/', admin_views.ReviewAdminListView.as_view(), name='admin_review_list'),
    path('manage/reviews/add/', admin_views.ReviewAdminCreateView.as_view(), name='admin_review_add'),
    path('manage/reviews/<int:pk>/edit/', admin_views.ReviewAdminUpdateView.as_view(), name='admin_review_edit'),
    path('manage/reviews/<int:pk>/delete/', admin_views.ReviewAdminDeleteView.as_view(), name='admin_review_delete'),
    path('manage/users/', admin_views.UserAdminListView.as_view(), name='admin_user_list'),
    path('manage/users/add/', admin_views.UserAdminCreateView.as_view(), name='admin_user_add'),
    path('manage/users/<int:pk>/', admin_views.UserAdminDetailView.as_view(), name='admin_user_detail'),
    path('manage/users/<int:pk>/password/', admin_views.UserAdminPasswordChangeView.as_view(), name='admin_user_password'),
    path('manage/groups/', admin_views.GroupAdminListView.as_view(), name='admin_group_list'),
    path('manage/groups/add/', admin_views.GroupAdminCreateView.as_view(), name='admin_group_add'),
    path('manage/groups/<int:pk>/edit/', admin_views.GroupAdminUpdateView.as_view(), name='admin_group_edit'),
    path('manage/groups/<int:pk>/delete/', admin_views.GroupAdminDeleteView.as_view(), name='admin_group_delete'),
    path('manage/profiles/', admin_views.UserProfileAdminListView.as_view(), name='admin_profile_list'),
    path('manage/spot-views/', admin_views.SpotViewAdminListView.as_view(), name='admin_spotview_list'),
]
