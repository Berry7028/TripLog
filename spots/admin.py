"""
Admin configuration for the Spots application.

This module registers models with the Django admin interface and customizes
their presentation (list views, filters, search fields, etc.).
"""

from django.contrib import admin

from .models import (
    Review,
    Spot,
    Tag,
    UserProfile,
    UserSpotInteraction,
)


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the Spot model.

    Customizes the list display, filtering, and field organization for Spots.
    """
    list_display = ['title', 'created_by', 'address', 'created_at']
    list_filter = ['created_at', 'created_by']
    search_fields = ['title', 'description', 'address']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['tags']
    
    fieldsets = (
        ('基本情報', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('位置情報', {
            'fields': ('latitude', 'longitude', 'address')
        }),
        ('画像', {
            'fields': ('image', 'image_url')
        }),
        ('タグ', {
            'fields': ('tags',),
        }),
        ('日時情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the Review model.

    Enables searching and filtering reviews by rating, user, and spot.
    """
    list_display = ['spot', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['spot__title', 'user__username', 'comment']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the UserProfile model.

    Manages user profiles including bio and favorite spots.
    """
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'bio']
    filter_horizontal = ['favorite_spots']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin view configuration for the Tag model.
    """
    list_display = ['name']
    search_fields = ['name']


@admin.register(UserSpotInteraction)
class UserSpotInteractionAdmin(admin.ModelAdmin):
    """
    Admin view configuration for UserSpotInteraction analytics.

    Displays user engagement metrics (views, duration) in the admin panel.
    """
    list_display = ['user', 'spot', 'view_count', 'total_view_duration', 'last_viewed_at']
    list_filter = ['last_viewed_at']
    search_fields = ['user__username', 'spot__title']
