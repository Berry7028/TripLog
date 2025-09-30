from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse


class Tag(models.Model):
    """スポットに付与するタグ"""
    name = models.CharField(max_length=50, unique=True, verbose_name='タグ名')

    class Meta:
        verbose_name = 'タグ'
        verbose_name_plural = 'タグ'
        ordering = ['name']

    def __str__(self):
        return self.name


class Spot(models.Model):
    """旅行スポットのモデル"""
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
    is_ai_generated = models.BooleanField(default=False, verbose_name='AI生成')
    
    class Meta:
        verbose_name = 'スポット'
        verbose_name_plural = 'スポット'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self) -> str:
        """スポット詳細ページのURLを返す"""
        return reverse('spot_detail', args=[self.id])

    @property
    def image_src(self) -> str:
        """アップロード画像のURLがあれば優先し、なければ外部の画像URLを返す"""
        if self.image:
            try:
                return self.image.url
            except Exception:
                # 画像が未設定の場合、Djangoはurlアクセスで例外を投げることがある
                pass
        return self.image_url or ''


class Review(models.Model):
    """スポットのレビューモデル"""
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
        unique_together = ['spot', 'user']  # 1つのスポットに対して1ユーザー1レビュー
    
    def __str__(self):
        return f'{self.spot.title} - {self.user.username} ({self.rating}★)'


class UserProfile(models.Model):
    """ユーザープロフィールの拡張モデル"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='ユーザー')
    bio = models.TextField(max_length=500, blank=True, verbose_name='自己紹介')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター')
    favorite_spots = models.ManyToManyField(Spot, blank=True, verbose_name='お気に入りスポット')
    
    class Meta:
        verbose_name = 'ユーザープロフィール'
        verbose_name_plural = 'ユーザープロフィール'
    
    def __str__(self):
        return f'{self.user.username}のプロフィール'


class SpotView(models.Model):
    """スポットの詳細ページ閲覧ログ（直近期間のランキング集計に利用）"""
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
        return f'{self.spot.title} @ {self.viewed_at}'


class UserSpotInteraction(models.Model):
    """ユーザーごとのスポット閲覧・滞在時間の分析用データ"""

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
        return f'{self.user.username} → {self.spot.title} ({self.view_count}回)'
