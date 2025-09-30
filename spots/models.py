from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
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


class RecommendationJobSetting(models.Model):
    """AIおすすめ解析のバックグラウンド実行設定。"""

    interval_hours = models.PositiveIntegerField(
        default=31,
        validators=[MinValueValidator(1)],
        verbose_name='解析間隔 (時間)',
        help_text='バックグラウンド解析を実行する間隔 (例: 31 時間ごと)。',
    )
    enabled = models.BooleanField(
        default=True,
        verbose_name='バックグラウンド解析を有効化',
    )
    last_run_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='最後に実行した日時',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')

    class Meta:
        verbose_name = 'おすすめ解析設定'
        verbose_name_plural = 'おすすめ解析設定'

    def __str__(self) -> str:
        status = '有効' if self.enabled else '停止中'
        return f'おすすめ解析 ({self.interval_hours}時間間隔, {status})'


class RecommendationJobLog(models.Model):
    """AI おすすめ解析の実行ログ。"""

    SOURCE_API = 'api'
    SOURCE_FALLBACK = 'fallback'
    SOURCE_NONE = 'none'

    TRIGGER_AUTO = 'auto'
    TRIGGER_ADMIN = 'admin'
    TRIGGER_CLI = 'cli'
    TRIGGER_API = 'api'

    SOURCE_CHOICES = [
        (SOURCE_API, 'API'),
        (SOURCE_FALLBACK, 'フォールバック'),
        (SOURCE_NONE, 'スコアなし'),
    ]
    TRIGGER_CHOICES = [
        (TRIGGER_AUTO, 'スケジュール'),
        (TRIGGER_ADMIN, '管理画面'),
        (TRIGGER_CLI, 'CLI'),
        (TRIGGER_API, 'API ツールコール'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recommendation_logs',
        verbose_name='対象ユーザー',
    )
    executed_at = models.DateTimeField(auto_now_add=True, verbose_name='実行日時')
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_NONE,
        verbose_name='スコア算出元',
    )
    triggered_by = models.CharField(
        max_length=20,
        choices=TRIGGER_CHOICES,
        default=TRIGGER_AUTO,
        verbose_name='実行トリガー',
    )
    scored_spot_ids = models.JSONField(
        default=list,
        blank=True,
        verbose_name='スコアリング対象スポットID',
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='追加メタ情報',
    )

    class Meta:
        verbose_name = 'おすすめ解析ログ'
        verbose_name_plural = 'おすすめ解析ログ'
        ordering = ['-executed_at']
        indexes = [
            models.Index(fields=['executed_at']),
            models.Index(fields=['user', 'executed_at']),
        ]

    def __str__(self) -> str:
        return f'{self.user.username} ({self.executed_at:%Y-%m-%d %H:%M})'

    @property
    def score_count(self) -> int:
        return len(self.scored_spot_ids or [])
