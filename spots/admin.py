from django.contrib import admin, messages

from .models import (
    RecommendationJobLog,
    RecommendationJobSetting,
    Review,
    Spot,
    Tag,
    UserProfile,
    UserRecommendationScore,
    UserSpotInteraction,
)
from .services import run_recommendation_for_user


@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    list_display = ["title", "created_by", "address", "created_at"]
    list_filter = ["created_at", "created_by"]
    search_fields = ["title", "description", "address"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["tags"]

    fieldsets = (
        ("基本情報", {"fields": ("title", "description", "created_by")}),
        ("位置情報", {"fields": ("latitude", "longitude", "address")}),
        ("画像", {"fields": ("image", "image_url")}),
        (
            "タグ",
            {
                "fields": ("tags",),
            },
        ),
        ("日時情報", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["spot", "user", "rating", "created_at"]
    list_filter = ["rating", "created_at"]
    search_fields = ["spot__title", "user__username", "comment"]
    readonly_fields = ["created_at"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "bio"]
    search_fields = ["user__username", "bio"]
    filter_horizontal = ["favorite_spots"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(UserSpotInteraction)
class UserSpotInteractionAdmin(admin.ModelAdmin):
    list_display = ["user", "spot", "view_count", "total_view_duration", "last_viewed_at"]
    list_filter = ["last_viewed_at"]
    search_fields = ["user__username", "spot__title"]
    actions = ["run_recommendation_analysis"]

    @admin.action(description="選択したユーザーの閲覧データをAIで解析")
    def run_recommendation_analysis(self, request, queryset):
        user_ids = set(queryset.values_list("user_id", flat=True))
        if not user_ids:
            self.message_user(request, "ユーザーが選択されていません。", level=messages.WARNING)
            return
        if len(user_ids) > 1:
            self.message_user(
                request,
                "複数ユーザーが選択されています。1ユーザーずつ実行してください。",
                level=messages.ERROR,
            )
            return

        user = queryset.first().user
        result = run_recommendation_for_user(
            user,
            triggered_by=RecommendationJobLog.TRIGGER_ADMIN,
            persist_log=True,
        )
        if result is None:
            self.message_user(
                request,
                f"{user.username} の閲覧データが見つからないため解析をスキップしました。",
                level=messages.WARNING,
            )
            return

        message = (
            f"{user.username} のおすすめ解析を実行しました。"
            f" スコアリング対象: {len(result.scored_spot_ids)} 件 (source={result.source})"
        )
        self.message_user(request, message, level=messages.SUCCESS)


@admin.register(RecommendationJobSetting)
class RecommendationJobSettingAdmin(admin.ModelAdmin):
    list_display = ["interval_hours", "enabled", "last_run_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]

    def has_add_permission(self, request):
        if RecommendationJobSetting.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(RecommendationJobLog)
class RecommendationJobLogAdmin(admin.ModelAdmin):
    list_display = ["user", "source", "triggered_by", "executed_at", "score_count"]
    list_filter = ["source", "triggered_by", "executed_at"]
    search_fields = ["user__username"]
    readonly_fields = [
        "user",
        "source",
        "triggered_by",
        "executed_at",
        "scored_spot_ids",
        "metadata",
    ]
    ordering = ["-executed_at"]


@admin.register(UserRecommendationScore)
class UserRecommendationScoreAdmin(admin.ModelAdmin):
    list_display = ["user", "spot", "score", "source", "updated_at"]
    list_filter = ["source", "updated_at"]
    search_fields = ["user__username", "spot__title"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-score", "-updated_at"]
