from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('ranking/', views.ranking, name='ranking'),
    path('spot/<int:spot_id>/', views.spot_detail, name='spot_detail'),
    path('spot/<int:spot_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('add/', views.add_spot, name='add_spot'),
    path('spot/<int:spot_id>/review/', views.add_review, name='add_review'),
    path('my-spots/', views.my_spots, name='my_spots'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    path('api/search/', views.search_spots_api, name='search_spots_api'),
    path('map/', views.map_view, name='map'),
    path('api/spots/', views.spots_api, name='spots_api'),
    path('api/spots/add/', views.add_spot_api, name='add_spot_api'),
    path('plan/', views.plan_view, name='plan'),
]
