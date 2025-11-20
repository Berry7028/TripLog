"""
Models for the TripLog application.

This module defines the database schemas for Spots, Reviews, User Profiles,
and analytics tracking such as SpotViews and UserSpotInteractions.
"""

from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse


class Tag(models.Model):
    """
    Represents a tag that can be attached to a spot.

    Attributes:
        name (str): The unique name of the tag.
    """
    name = models.CharField(max_length=50, unique=True, verbose_name='タグ名')

    class Meta:
        verbose_name = 'タグ'
        verbose_name_plural = 'タグ'
        ordering = ['name']

    def __str__(self):
        """Returns the string representation of the Tag (its name)."""
        return self.name


class Spot(models.Model):
    """
    Represents a travel spot or destination.

    Attributes:
        title (str): The name of the spot.
        description (str): Detailed description of the spot.
        latitude (float): The geographical latitude.
        longitude (float): The geographical longitude.
        address (str): The physical address (optional).
        image (ImageField): Uploaded image of the spot (optional).
        image_url (str): External URL to an image (optional).
        created_by (User): The user who created this spot entry.
        created_at (datetime): When the spot was created.
        updated_at (datetime): When the spot was last updated.
        tags (ManyToManyField): Tags associated with the spot.
    """
    title = models.CharField(max_length=200, verbose_name='スポット名')
    description = models.TextField(verbose_name='説明')
    latitude = models.FloatField(verbose_name='緯度')
    longitude = models.FloatField(verbose_name='経度')
    address = models.CharField(max_length=300, verbose_name='住所', blank=True)
    image = models.ImageField(upload_to='spot_images/', verbose_name='画像', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True, verbose_name='画像URL')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='投稿者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    tags = models.ManyToManyField(Tag, blank=True, related_name='spots', verbose_name='タグ')

    class Meta:
        verbose_name = 'スポット'
        verbose_name_plural = 'スポット'
        ordering = ['-created_at']

    def __str__(self):
        """Returns the string representation of the Spot (its title)."""
        return self.title

    def get_absolute_url(self) -> str:
        """
        Returns the URL to the spot's detail page.

        Returns:
            str: The relative URL path for the spot detail view.
        """
        return reverse('spot_detail', args=[self.id])

    @property
    def image_src(self) -> str:
        """
        Determines the image source URL for the spot.

        Prioritizes the uploaded image URL if available. If not, falls back to
        the external `image_url`. Returns an empty string if neither exists.

        Returns:
            str: The URL string for the image.
        """
        if self.image:
            try:
                return self.image.url
            except Exception:
                # Django may raise an exception if the file is missing
                pass
        return self.image_url or ''


class Review(models.Model):
    """
    Represents a user review for a specific spot.

    Attributes:
        spot (Spot): The spot being reviewed.
        user (User): The user who wrote the review.
        rating (int): Rating value between 1 and 5.
        comment (str): Text content of the review.
        created_at (datetime): When the review was created.
    """
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='reviews', verbose_name='スポット')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='レビュー者')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='評価'
    )
    comment = models.TextField(verbose_name='コメント')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    
    class Meta:
        verbose_name = 'レビュー'
        verbose_name_plural = 'レビュー'
        ordering = ['-created_at']
        unique_together = ['spot', 'user']  # One review per user per spot
    
    def __str__(self):
        """Returns a summary string of the review."""
        return f'{self.spot.title} - {self.user.username} ({self.rating}★)'


class UserProfile(models.Model):
    """
    Extends the default User model with additional profile information.

    Attributes:
        user (User): The associated User instance.
        bio (str): User's biography or self-introduction.
        avatar (ImageField): User's profile picture.
        favorite_spots (ManyToManyField): Collection of spots marked as favorites.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    bio = models.TextField(max_length=500, blank=True, verbose_name='自己紹介')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター')
    favorite_spots = models.ManyToManyField(Spot, blank=True, verbose_name='お気に入りスポット')
    
    class Meta:
        verbose_name = 'ユーザープロフィール'
        verbose_name_plural = 'ユーザープロフィール'
    
    def __str__(self):
        """Returns the string representation of the profile."""
        return f'{self.user.username}のプロフィール'


class SpotView(models.Model):
    """
    Logs individual page views for spots.

    This model is primarily used for calculating popularity or trending rankings
    over a recent time period (e.g., weekly views).

    Attributes:
        spot (Spot): The spot that was viewed.
        viewed_at (datetime): Timestamp of the view event.
    """
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='spot_views', verbose_name='スポット')
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name='閲覧日時')

    class Meta:
        verbose_name = 'スポット閲覧ログ'
        verbose_name_plural = 'スポット閲覧ログ'
        indexes = [
            models.Index(fields=['viewed_at']),
            models.Index(fields=['spot', 'viewed_at']),
        ]

    def __str__(self) -> str:
        """Returns a summary string of the view log."""
        return f'{self.spot.title} @ {self.viewed_at}'


class UserSpotInteraction(models.Model):
    """
    Aggregated analytics data for user interactions with a specific spot.

    Tracks how many times a specific user has viewed a spot and the total
    duration they have spent on the page.

    Attributes:
        user (User): The user interacting with the spot.
        spot (Spot): The spot being interacted with.
        view_count (int): Number of times the user viewed the spot.
        total_view_duration (timedelta): Cumulative time spent viewing the spot.
        last_viewed_at (datetime): Timestamp of the most recent interaction.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='spot_interactions',
        verbose_name='ユーザー',
    )
    spot = models.ForeignKey(
        Spot,
        on_delete=models.CASCADE,
        related_name='user_interactions',
        verbose_name='スポット',
    )
    view_count = models.PositiveIntegerField(default=0, verbose_name='閲覧回数')
    total_view_duration = models.DurationField(
        default=timedelta,
        verbose_name='累積滞在時間',
    )
    last_viewed_at = models.DateTimeField(auto_now=True, verbose_name='最終閲覧日時')

    class Meta:
        verbose_name = 'ユーザー閲覧データ'
        verbose_name_plural = 'ユーザー閲覧データ'
        unique_together = ('user', 'spot')
        indexes = [
            models.Index(fields=['user', 'spot']),
            models.Index(fields=['-last_viewed_at']),
        ]

    def __str__(self) -> str:
        """Returns a summary string of the interaction."""
        return f'{self.user.username} → {self.spot.title} ({self.view_count}回)'
