from django.urls import path, include

from . import views

urlpatterns = [

    ## debug
    path("__reload__/", include("django_browser_reload.urls")),


    # ホーム・ランキング・ユーザー関連
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('ranking/', views.ranking, name='ranking'),
    path('licenses/', views.licenses, name='licenses'),
    path('my-spots/', views.my_spots, name='my_spots'),
    path('profile/', views.profile, name='profile'),
    path('users/<str:username>/', views.user_profile, name='user_profile'),

    # スポット詳細・操作
    path('spot/<int:spot_id>/', views.spot_detail, name='spot_detail'),
    path('spot/<int:spot_id>/edit/', views.edit_spot, name='edit_spot'),
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
]
