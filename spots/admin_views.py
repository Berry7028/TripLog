"""スタッフ向けのカスタム管理ダッシュボード用ビュー群。"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import (
    GroupAdminForm,
    ReviewAdminForm,
    SpotAdminForm,
    TagForm,
    UserAdminCreateForm,
    UserAdminForm,
    UserProfileAdminForm,
)
from .models import (
    RecommendationJobLog,
    RecommendationJobSetting,
    Review,
    Spot,
    SpotView,
    Tag,
    UserProfile,
    UserRecommendationScore,
)
from .services import compute_and_store_all_user_scores


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """is_staffユーザーのみ許可するMixin"""

    login_url = "login"

    def test_func(self) -> bool:
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "管理者権限が必要です。")
            return redirect("home")
        return super().handle_no_permission()


class AdminPermissionRequiredMixin(StaffRequiredMixin):
    """スタッフの中でも特定の権限を要求するMixin"""

    required_permissions: tuple[str, ...] = ()

    def get_required_permissions(self) -> tuple[str, ...]:
        return self.required_permissions

    def test_func(self) -> bool:
        if not super().test_func():
            return False
        user = self.request.user
        if user.is_superuser:
            return True
        perms = self.get_required_permissions()
        if not perms:
            return True
        return user.has_perms(perms)


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """管理ダッシュボードトップ"""

    template_name = "spots/admin/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        context.update(
            {
                "total_spots": Spot.objects.count(),
                "total_reviews": Review.objects.count(),
                "total_users": User.objects.count(),
                "total_tags": Tag.objects.count(),
                "views_last_week": SpotView.objects.filter(viewed_at__gte=week_ago).count(),
                "ai_scores_count": UserRecommendationScore.objects.count(),
                "new_spots": Spot.objects.select_related("created_by")
                .prefetch_related("tags")
                .order_by("-created_at")[:5],
                "recent_reviews": Review.objects.select_related("spot", "user").order_by(
                    "-created_at"
                )[:5],
                "top_spots": Spot.objects.annotate(
                    weekly_views=Count(
                        "spot_views",
                        filter=Q(spot_views__viewed_at__gte=week_ago),
                        distinct=True,
                    ),
                    review_avg=Avg("reviews__rating"),
                )
                .select_related("created_by")
                .order_by("-weekly_views", "-created_at")[:5],
                "popular_tags": Tag.objects.annotate(
                    spot_count=Count("spots", distinct=True)
                ).order_by("-spot_count", "name")[:10],
                "top_reviewers": User.objects.annotate(review_count=Count("review", distinct=True))
                .filter(review_count__gt=0)
                .order_by("-review_count", "username")[:5],
                "ai_generated_spots": Spot.objects.filter(is_ai_generated=True)
                .select_related("created_by")
                .order_by("-updated_at")[:5],
            }
        )
        return context


class SpotAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/spot_list.html"
    model = Spot
    context_object_name = "spots"
    paginate_by = 20
    ordering = ["-created_at"]

    def get_queryset(self):
        week_ago = timezone.now() - timedelta(days=7)
        queryset = (
            Spot.objects.select_related("created_by")
            .prefetch_related("tags")
            .annotate(
                review_count=Count("reviews", distinct=True),
                weekly_views=Count(
                    "spot_views",
                    filter=Q(spot_views__viewed_at__gte=week_ago),
                    distinct=True,
                ),
            )
        )
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(address__icontains=search)
                | Q(tags__name__icontains=search)
            ).distinct()
        tag_id = self.request.GET.get("tag")
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        creator_id = self.request.GET.get("creator")
        if creator_id:
            queryset = queryset.filter(created_by__id=creator_id)
        ai_flag = self.request.GET.get("ai")
        if ai_flag == "1":
            queryset = queryset.filter(is_ai_generated=True)
        elif ai_flag == "0":
            queryset = queryset.filter(is_ai_generated=False)
        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "search_query": self.request.GET.get("q", "").strip(),
                "selected_tag": self.request.GET.get("tag", ""),
                "selected_creator": self.request.GET.get("creator", ""),
                "selected_ai": self.request.GET.get("ai", ""),
                "tags": Tag.objects.order_by("name"),
                "creators": User.objects.order_by("username"),
            }
        )
        return context


class SpotAdminCreateView(StaffRequiredMixin, CreateView):
    model = Spot
    form_class = SpotAdminForm
    template_name = "spots/admin/spot_form.html"
    success_url = reverse_lazy("admin_spot_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "スポットを作成しました。")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class SpotAdminUpdateView(StaffRequiredMixin, UpdateView):
    model = Spot
    form_class = SpotAdminForm
    template_name = "spots/admin/spot_form.html"
    success_url = reverse_lazy("admin_spot_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "スポットを更新しました。")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class SpotAdminDeleteView(StaffRequiredMixin, DeleteView):
    model = Spot
    template_name = "spots/admin/spot_confirm_delete.html"
    success_url = reverse_lazy("admin_spot_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "スポットを削除しました。")
        return super().delete(request, *args, **kwargs)


class TagAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/tag_list.html"
    model = Tag
    context_object_name = "tags"
    paginate_by = 30
    ordering = ["name"]

    def get_queryset(self):
        queryset = Tag.objects.annotate(spot_count=Count("spots", distinct=True))
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class TagAdminCreateView(StaffRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = "spots/admin/tag_form.html"
    success_url = reverse_lazy("admin_tag_list")

    def form_valid(self, form):
        messages.success(self.request, "タグを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class TagAdminUpdateView(StaffRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = "spots/admin/tag_form.html"
    success_url = reverse_lazy("admin_tag_list")

    def form_valid(self, form):
        messages.success(self.request, "タグを更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class TagAdminDeleteView(StaffRequiredMixin, DeleteView):
    model = Tag
    template_name = "spots/admin/tag_confirm_delete.html"
    success_url = reverse_lazy("admin_tag_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "タグを削除しました。")
        return super().delete(request, *args, **kwargs)


class ReviewAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/review_list.html"
    model = Review
    context_object_name = "reviews"
    paginate_by = 25
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Review.objects.select_related("spot", "user").order_by("-created_at")
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(spot__title__icontains=search)
                | Q(user__username__icontains=search)
                | Q(comment__icontains=search)
            )
        rating = self.request.GET.get("rating")
        if rating:
            queryset = queryset.filter(rating=rating)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "search_query": self.request.GET.get("q", "").strip(),
                "selected_rating": self.request.GET.get("rating", ""),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")
        selected_ids = request.POST.getlist("selected")
        if action == "delete_selected" and selected_ids:
            deleted_count, _ = Review.objects.filter(pk__in=selected_ids).delete()
            messages.success(request, f"{deleted_count}件のレビューを削除しました。")
        else:
            messages.info(request, "操作対象が選択されていません。")
        return redirect("admin_review_list")


class ReviewAdminUpdateView(StaffRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewAdminForm
    template_name = "spots/admin/review_form.html"
    success_url = reverse_lazy("admin_review_list")

    def form_valid(self, form):
        messages.success(self.request, "レビューを更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class ReviewAdminCreateView(StaffRequiredMixin, CreateView):
    model = Review
    form_class = ReviewAdminForm
    template_name = "spots/admin/review_form.html"
    success_url = reverse_lazy("admin_review_list")

    def form_valid(self, form):
        messages.success(self.request, "レビューを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class ReviewAdminDeleteView(StaffRequiredMixin, DeleteView):
    model = Review
    template_name = "spots/admin/review_confirm_delete.html"
    success_url = reverse_lazy("admin_review_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "レビューを削除しました。")
        return super().delete(request, *args, **kwargs)


class UserAdminListView(AdminPermissionRequiredMixin, ListView):
    template_name = "spots/admin/user_list.html"
    model = User
    context_object_name = "users"
    paginate_by = 25
    ordering = ["username"]
    required_permissions = ("auth.view_user",)

    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        staff_filter = self.request.GET.get("staff")
        if staff_filter == "1":
            queryset = queryset.filter(is_staff=True)
        elif staff_filter == "0":
            queryset = queryset.filter(is_staff=False)
        active_filter = self.request.GET.get("active")
        if active_filter == "1":
            queryset = queryset.filter(is_active=True)
        elif active_filter == "0":
            queryset = queryset.filter(is_active=False)
        return queryset.order_by("username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "search_query": self.request.GET.get("q", "").strip(),
                "selected_staff": self.request.GET.get("staff", ""),
                "selected_active": self.request.GET.get("active", ""),
            }
        )
        return context


class UserAdminCreateView(AdminPermissionRequiredMixin, CreateView):
    model = User
    form_class = UserAdminCreateForm
    template_name = "spots/admin/user_form.html"
    success_url = reverse_lazy("admin_user_list")
    required_permissions = ("auth.add_user",)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request_user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "ユーザーを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class UserAdminDetailView(AdminPermissionRequiredMixin, TemplateView):
    template_name = "spots/admin/user_detail.html"

    def get_required_permissions(self) -> tuple[str, ...]:
        if self.request.method.upper() == "POST":
            return ("auth.change_user",)
        return ("auth.view_user",)

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.user_obj)
        context.update(
            {
                "user_obj": self.user_obj,
                "profile": profile,
                "user_form": kwargs.get("user_form")
                or UserAdminForm(instance=self.user_obj, request_user=self.request.user),
                "profile_form": kwargs.get("profile_form")
                or UserProfileAdminForm(instance=profile),
                "recent_spots": self.user_obj.spot_set.select_related("created_by").order_by(
                    "-created_at"
                )[:5],
                "recent_reviews": self.user_obj.review_set.select_related("spot").order_by(
                    "-created_at"
                )[:5],
                "available_permissions": Permission.objects.order_by(
                    "content_type__app_label", "codename"
                ),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        profile, _ = UserProfile.objects.get_or_create(user=self.user_obj)
        user_form = UserAdminForm(
            request.POST,
            instance=self.user_obj,
            request_user=request.user,
        )
        profile_form = UserProfileAdminForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "ユーザー情報を更新しました。")
            return redirect("admin_user_detail", pk=self.user_obj.pk)
        messages.error(request, "入力内容を確認してください。")
        context = self.get_context_data(user_form=user_form, profile_form=profile_form)
        return self.render_to_response(context)


class UserAdminPasswordChangeView(AdminPermissionRequiredMixin, FormView):
    template_name = "spots/admin/user_password.html"
    form_class = AdminPasswordChangeForm
    required_permissions = ("auth.change_user",)

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = self.form_class(user=self.user_obj, data=self.request.POST or None)
        for field in form.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
        return form

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "パスワードを更新しました。")
        return redirect("admin_user_detail", pk=self.user_obj.pk)

    def form_invalid(self, form):
        messages.error(self.request, "パスワードを更新できませんでした。")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"user_obj": self.user_obj})
        return context


class GroupAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/group_list.html"
    model = Group
    context_object_name = "groups"
    paginate_by = 25
    ordering = ["name"]

    def get_queryset(self):
        queryset = Group.objects.all()
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class GroupAdminCreateView(StaffRequiredMixin, CreateView):
    model = Group
    form_class = GroupAdminForm
    template_name = "spots/admin/group_form.html"
    success_url = reverse_lazy("admin_group_list")

    def form_valid(self, form):
        messages.success(self.request, "グループを作成しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class GroupAdminUpdateView(StaffRequiredMixin, UpdateView):
    model = Group
    form_class = GroupAdminForm
    template_name = "spots/admin/group_form.html"
    success_url = reverse_lazy("admin_group_list")

    def form_valid(self, form):
        messages.success(self.request, "グループを更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "入力内容を確認してください。")
        return super().form_invalid(form)


class GroupAdminDeleteView(StaffRequiredMixin, DeleteView):
    model = Group
    template_name = "spots/admin/group_confirm_delete.html"
    success_url = reverse_lazy("admin_group_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "グループを削除しました。")
        return super().delete(request, *args, **kwargs)


class UserProfileAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/profile_list.html"
    model = UserProfile
    context_object_name = "profiles"
    paginate_by = 25
    ordering = ["user__username"]

    def get_queryset(self):
        queryset = UserProfile.objects.select_related("user").prefetch_related("favorite_spots")
        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(bio__icontains=search)
                | Q(favorite_spots__title__icontains=search)
            ).distinct()
        return queryset.order_by("user__username")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        return context


class SpotViewAdminListView(StaffRequiredMixin, ListView):
    template_name = "spots/admin/spotview_list.html"
    model = SpotView
    context_object_name = "logs"
    paginate_by = 50
    ordering = ["-viewed_at"]

    def get_queryset(self):
        queryset = SpotView.objects.select_related("spot").order_by("-viewed_at")
        spot_id = self.request.GET.get("spot")
        if spot_id:
            queryset = queryset.filter(spot_id=spot_id)
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        if date_from:
            queryset = queryset.filter(viewed_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(viewed_at__date__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "spots": Spot.objects.order_by("title"),
                "selected_spot": self.request.GET.get("spot", ""),
                "date_from": self.request.GET.get("date_from", ""),
                "date_to": self.request.GET.get("date_to", ""),
            }
        )
        return context


@dataclass
class UserScoreEntry:
    """ユーザーごとのスポットスコアをテンプレート描画用に整形したエントリ。"""

    id: int
    spot_id: int
    spot_title: str
    score: float
    source: str
    updated_at: datetime
    reason: str


@dataclass
class UserScoreFolder:
    """ユーザー単位でスコアを束ねたフォルダー情報。"""

    user: User
    scores: List[UserScoreEntry]
    score_count: int
    last_updated: Optional[datetime]
    top_score: Optional[float]


class RecommendationAdminView(StaffRequiredMixin, TemplateView):
    """AIおすすめ解析の管理画面"""

    template_name = "spots/admin/recommendation_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 設定情報を取得
        from .services import get_or_create_job_setting

        setting = get_or_create_job_setting()

        # 統計情報
        total_scores = UserRecommendationScore.objects.count()
        users_with_scores = UserRecommendationScore.objects.values("user").distinct().count()
        recent_logs = RecommendationJobLog.objects.select_related("user").order_by("-executed_at")[
            :10
        ]

        # ユーザー別のスコア数
        from django.db.models import Count

        user_score_stats = (
            UserRecommendationScore.objects.values("user__username", "user__id")
            .annotate(score_count=Count("id"))
            .order_by("-score_count")[:10]
        )

        context.update(
            {
                "setting": setting,
                "total_scores": total_scores,
                "users_with_scores": users_with_scores,
                "recent_logs": recent_logs,
                "user_score_stats": user_score_stats,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        if action == "run_all":
            # 全ユーザーのスコア計算を実行
            try:
                result = compute_and_store_all_user_scores(
                    triggered_by=RecommendationJobLog.TRIGGER_ADMIN
                )
                if result["success"]:
                    messages.success(
                        request,
                        f'✓ {result["users_processed"]}ユーザーを処理し、'
                        f'{result["scores_saved"]}件のスコアを保存しました。',
                    )
                else:
                    messages.warning(
                        request, f'一部エラーが発生しました: {len(result.get("errors", []))}件'
                    )
            except Exception as e:
                messages.error(request, f"エラーが発生しました: {str(e)}")

        elif action == "update_setting":
            # 設定を更新
            from .services import get_or_create_job_setting

            setting = get_or_create_job_setting()
            interval_hours = request.POST.get("interval_hours")
            enabled = request.POST.get("enabled") == "on"

            try:
                setting.interval_hours = int(interval_hours)
                setting.enabled = enabled
                setting.save()
                messages.success(request, "設定を更新しました。")
            except ValueError:
                messages.error(request, "間隔は数値で入力してください。")

        return redirect("admin_recommendation")


class RecommendationUserScoreListView(StaffRequiredMixin, TemplateView):
    """ユーザーごとにフォルダー形式でスコアを閲覧できる管理画面。"""

    template_name = "spots/admin/recommendation_scores.html"

    def _get_filter_values(self) -> Dict[str, str]:
        request = self.request
        return {
            "user": request.GET.get("user", "").strip(),
            "spot": request.GET.get("spot", "").strip(),
            "source": request.GET.get("source", "").strip(),
            "min_score": request.GET.get("min_score", "").strip(),
            "query": request.GET.get("q", "").strip(),
        }

    def _apply_filters(
        self,
        queryset,
        filters: Dict[str, str],
    ) -> tuple[List[UserRecommendationScore], List[str]]:
        filter_errors: List[str] = []
        qs = queryset

        if filters["user"]:
            try:
                qs = qs.filter(user_id=int(filters["user"]))
            except ValueError:
                filter_errors.append("ユーザーIDは数値で指定してください。")

        if filters["spot"]:
            try:
                qs = qs.filter(spot_id=int(filters["spot"]))
            except ValueError:
                filter_errors.append("スポットIDは数値で指定してください。")

        if filters["source"]:
            qs = qs.filter(source=filters["source"])

        if filters["min_score"]:
            try:
                min_score_value = float(filters["min_score"])
            except ValueError:
                filter_errors.append("最小スコアは数値で指定してください。")
            else:
                qs = qs.filter(score__gte=min_score_value)

        if filters["query"]:
            query = filters["query"]
            qs = qs.filter(
                Q(user__username__icontains=query)
                | Q(spot__title__icontains=query)
                | Q(spot__description__icontains=query)
            )

        score_list = list(
            qs.select_related("user", "spot").order_by("user__username", "-score", "-updated_at")
        )
        return score_list, filter_errors

    def _build_user_folders(
        self,
        scores: List[UserRecommendationScore],
    ) -> List[UserScoreFolder]:
        folders: "OrderedDict[int, UserScoreFolder]" = OrderedDict()

        for score in scores:
            entry = UserScoreEntry(
                id=score.id,
                spot_id=score.spot_id,
                spot_title=score.spot.title,
                score=round(float(score.score), 4),
                source=score.source,
                updated_at=score.updated_at,
                reason=score.reason,
            )

            folder = folders.get(score.user_id)
            if folder is None:
                folder = UserScoreFolder(
                    user=score.user,
                    scores=[entry],
                    score_count=1,
                    last_updated=score.updated_at,
                    top_score=entry.score,
                )
                folders[score.user_id] = folder
            else:
                folder.scores.append(entry)
                folder.score_count += 1
                if folder.last_updated is None or score.updated_at > folder.last_updated:
                    folder.last_updated = score.updated_at
                if folder.top_score is None or entry.score > folder.top_score:
                    folder.top_score = entry.score

        return list(folders.values())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filters = self._get_filter_values()

        base_queryset = UserRecommendationScore.objects.all()
        score_list, filter_errors = self._apply_filters(base_queryset, filters)
        user_folders = self._build_user_folders(score_list)

        total_scores = len(score_list)
        folder_count = len(user_folders)

        source_choices = list(
            UserRecommendationScore.objects.order_by("source")
            .values_list("source", flat=True)
            .distinct()
        )

        context.update(
            {
                "user_folders": user_folders,
                "folder_count": folder_count,
                "total_scores": total_scores,
                "filters": filters,
                "filter_errors": filter_errors,
                "users": User.objects.filter(recommendation_scores__isnull=False)
                .distinct()
                .order_by("username"),
                "spots": Spot.objects.order_by("title"),
                "source_choices": source_choices,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get("action")

        filter_map = {
            "user": "user",
            "spot": "spot",
            "source": "source",
            "min_score": "min_score",
            "query": "q",
        }
        preserved_params = {}
        for context_key, param_name in filter_map.items():
            value = request.POST.get(f"filter__{context_key}", "").strip()
            if value:
                preserved_params[param_name] = value

        redirect_url = request.path
        if preserved_params:
            redirect_url = f"{redirect_url}?{urlencode(preserved_params)}"

        if action == "delete_selected":
            selected_ids = request.POST.getlist("selected")
            if selected_ids:
                deleted_count, _ = UserRecommendationScore.objects.filter(
                    pk__in=selected_ids
                ).delete()
                messages.success(request, f"{deleted_count}件のスコアを削除しました。")
            else:
                messages.warning(request, "削除対象が選択されていません。")

        elif action == "delete_user_scores":
            user_id = request.POST.get("user_id")
            if user_id:
                deleted_count, _ = UserRecommendationScore.objects.filter(user_id=user_id).delete()
                messages.success(request, f"{deleted_count}件のスコアを削除しました。")

        elif action == "recalculate_user":
            user_id = request.POST.get("user_id")
            if user_id:
                from .services import run_recommendation_for_user

                user = User.objects.filter(id=user_id).first()
                if user:
                    try:
                        from .models import Spot

                        all_spots = list(Spot.objects.all().prefetch_related("tags"))
                        from .services.recommendation_jobs import _compute_and_store_user_scores

                        result = _compute_and_store_user_scores(
                            user=user,
                            all_spots=all_spots,
                            triggered_by=RecommendationJobLog.TRIGGER_ADMIN,
                        )
                        if result:
                            messages.success(
                                request,
                                f"{user.username} のスコアを再計算しました: "
                                f'{result["scores_saved"]}件保存',
                            )
                        else:
                            messages.warning(request, f"{user.username} の閲覧履歴がありません。")
                    except Exception as e:
                        messages.error(request, f"エラー: {str(e)}")

        return redirect(redirect_url)


class RecommendationJobLogListView(StaffRequiredMixin, ListView):
    """AIおすすめ解析の実行ログ一覧"""

    template_name = "spots/admin/recommendation_logs.html"
    model = RecommendationJobLog
    context_object_name = "logs"
    paginate_by = 50
    ordering = ["-executed_at"]

    def get_queryset(self):
        queryset = RecommendationJobLog.objects.select_related("user").order_by("-executed_at")

        user_id = self.request.GET.get("user")
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        source = self.request.GET.get("source")
        if source:
            queryset = queryset.filter(source=source)

        triggered_by = self.request.GET.get("triggered_by")
        if triggered_by:
            queryset = queryset.filter(triggered_by=triggered_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "users": User.objects.order_by("username"),
                "selected_user": self.request.GET.get("user", ""),
                "selected_source": self.request.GET.get("source", ""),
                "selected_triggered_by": self.request.GET.get("triggered_by", ""),
                "source_choices": RecommendationJobLog.SOURCE_CHOICES,
                "trigger_choices": RecommendationJobLog.TRIGGER_CHOICES,
            }
        )
        return context
