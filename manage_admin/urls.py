from django.urls import path

from . import views

urlpatterns = [
    # 管理ダッシュボード
    path('', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('spots/', views.SpotAdminListView.as_view(), name='admin_spot_list'),
    path('spots/add/', views.SpotAdminCreateView.as_view(), name='admin_spot_add'),
    path('spots/<int:pk>/edit/', views.SpotAdminUpdateView.as_view(), name='admin_spot_edit'),
    path('spots/<int:pk>/delete/', views.SpotAdminDeleteView.as_view(), name='admin_spot_delete'),
    path('tags/', views.TagAdminListView.as_view(), name='admin_tag_list'),
    path('tags/add/', views.TagAdminCreateView.as_view(), name='admin_tag_add'),
    path('tags/<int:pk>/edit/', views.TagAdminUpdateView.as_view(), name='admin_tag_edit'),
    path('tags/<int:pk>/delete/', views.TagAdminDeleteView.as_view(), name='admin_tag_delete'),
    path('reviews/', views.ReviewAdminListView.as_view(), name='admin_review_list'),
    path('reviews/add/', views.ReviewAdminCreateView.as_view(), name='admin_review_add'),
    path('reviews/<int:pk>/edit/', views.ReviewAdminUpdateView.as_view(), name='admin_review_edit'),
    path('reviews/<int:pk>/delete/', views.ReviewAdminDeleteView.as_view(), name='admin_review_delete'),
    path('users/', views.UserAdminListView.as_view(), name='admin_user_list'),
    path('users/add/', views.UserAdminCreateView.as_view(), name='admin_user_add'),
    path('users/<int:pk>/', views.UserAdminDetailView.as_view(), name='admin_user_detail'),
    path('users/<int:pk>/password/', views.UserAdminPasswordChangeView.as_view(), name='admin_user_password'),
    path('groups/', views.GroupAdminListView.as_view(), name='admin_group_list'),
    path('groups/add/', views.GroupAdminCreateView.as_view(), name='admin_group_add'),
    path('groups/<int:pk>/edit/', views.GroupAdminUpdateView.as_view(), name='admin_group_edit'),
    path('groups/<int:pk>/delete/', views.GroupAdminDeleteView.as_view(), name='admin_group_delete'),
    path('profiles/', views.UserProfileAdminListView.as_view(), name='admin_profile_list'),
    path('spot-views/', views.SpotViewAdminListView.as_view(), name='admin_spotview_list'),
]
