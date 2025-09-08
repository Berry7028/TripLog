from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Spot(models.Model):
    """旅行スポットのモデル"""
    title = models.CharField(max_length=200, verbose_name='スポット名')
    description = models.TextField(verbose_name='説明')
    latitude = models.FloatField(verbose_name='緯度')
    longitude = models.FloatField(verbose_name='経度')
    address = models.CharField(max_length=300, verbose_name='住所', blank=True)
    image = models.ImageField(upload_to='spot_images/', verbose_name='画像', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='投稿者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    class Meta:
        verbose_name = 'スポット'
        verbose_name_plural = 'スポット'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Review(models.Model):
    """スポットのレビューモデル"""
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE, related_name='reviews', verbose_name='スポット')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='レビュー者')
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
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='ユーザー')
    bio = models.TextField(max_length=500, blank=True, verbose_name='自己紹介')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='アバター')
    favorite_spots = models.ManyToManyField(Spot, blank=True, verbose_name='お気に入りスポット')
    
    class Meta:
        verbose_name = 'ユーザープロフィール'
        verbose_name_plural = 'ユーザープロフィール'
    
    def __str__(self):
        return f'{self.user.username}のプロフィール'
