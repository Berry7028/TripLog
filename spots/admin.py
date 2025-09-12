from django.contrib import admin
from .models import Spot, Review, UserProfile, Tag


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
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
            'fields': ('image',)
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
    list_display = ['spot', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['spot__title', 'user__username', 'comment']
    readonly_fields = ['created_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio']
    search_fields = ['user__username', 'bio']
    filter_horizontal = ['favorite_spots']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
