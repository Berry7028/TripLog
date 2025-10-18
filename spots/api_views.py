"""Next.jsフロントエンド向けのJSON APIビュー。"""

from __future__ import annotations

import json
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import ReviewForm, SpotForm, UserProfileForm
from .models import Review, Spot, UserProfile
from .services.homepage import fetch_homepage_spots
from .services.interactions import (
    fetch_related_spots,
    is_favorite_spot,
    log_spot_view,
    toggle_favorite_spot,
    update_view_duration,
)
from .services.serializers import (
    serialize_review,
    serialize_review_activity,
    serialize_spot_brief,
    serialize_spot_detail,
    serialize_spot_summary,
    serialize_user_profile,
)


@require_GET
def home_data(request):
    """ホーム画面のスポット一覧を返す。"""

    result = fetch_homepage_spots(
        user=request.user,
        search_query=request.GET.get("search", ""),
        sort_mode=request.GET.get("sort", "recent"),
    )

    paginator = Paginator(result.spots, 12)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    spots_payload = []
    recommendation_ids = set(result.recommendation_scored_ids or [])
    for spot in page_obj.object_list:
        data = serialize_spot_summary(spot)
        data["is_recommended"] = (
            result.sort_mode == "relevance" and spot.id in recommendation_ids
        )
        spots_payload.append(data)

    return JsonResponse(
        {
            "spots": spots_payload,
            "pagination": {
                "page": page_obj.number,
                "pages": paginator.num_pages,
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "total_count": paginator.count,
            },
            "search_query": result.search_query,
            "sort_mode": result.sort_mode,
            "recommendation_source": result.recommendation_source,
            "recommendation_notice": result.recommendation_notice,
            "recommendation_scored_ids": list(recommendation_ids),
            "viewer_is_authenticated": getattr(
                request.user, "is_authenticated", False
            ),
        }
    )


@require_GET
def spot_detail_data(request, spot_id: int):
    """スポット詳細情報を返す。"""

    spot = get_object_or_404(Spot.objects.select_related("created_by"), id=spot_id)
    log_spot_view(spot, request.user)

    reviews_qs = spot.reviews.select_related("user").all()
    avg_rating = reviews_qs.aggregate(Avg("rating"))["rating__avg"]

    is_favorite = is_favorite_spot(spot, request.user)
    viewer_can_review = False
    if getattr(request.user, "is_authenticated", False):
        viewer_can_review = not reviews_qs.filter(user=request.user).exists()

    related_spots = fetch_related_spots(spot)

    return JsonResponse(
        {
            "spot": serialize_spot_detail(spot),
            "share_url": request.build_absolute_uri(spot.get_absolute_url()),
            "reviews": [serialize_review(review) for review in reviews_qs],
            "avg_rating": avg_rating,
            "is_favorite": is_favorite,
            "viewer": {
                "is_authenticated": getattr(request.user, "is_authenticated", False),
                "can_review": viewer_can_review,
            },
            "related_spots": [serialize_spot_summary(item) for item in related_spots],
        }
    )


@require_GET
def ranking_data(request):
    """ランキングデータを返す。"""

    week_ago = timezone.now() - timedelta(days=7)
    ranked_spots = (
        Spot.objects.all()
        .annotate(
            weekly_views=Count(
                "spot_views", filter=Q(spot_views__viewed_at__gte=week_ago)
            )
        )
        .filter(weekly_views__gt=0)
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-weekly_views", "-created_at")
    )
    return JsonResponse(
        {
            "week_ago": week_ago.isoformat(),
            "spots": [
                {
                    **serialize_spot_summary(spot),
                    "weekly_views": spot.weekly_views,
                }
                for spot in ranked_spots[:7]
            ],
        }
    )


@require_GET
def auth_status(request):
    """ログイン状態を返す。"""

    if not getattr(request.user, "is_authenticated", False):
        return JsonResponse({"is_authenticated": False})

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    user_spots = (
        request.user.spot_set.select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    user_reviews = (
        request.user.review_set.select_related("spot")
        .order_by("-created_at")
    )
    return JsonResponse(
        {
            "is_authenticated": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
                "date_joined": request.user.date_joined.isoformat()
                if request.user.date_joined
                else None,
                "profile": serialize_user_profile(profile),
            },
            "stats": {
                "spot_count": user_spots.count(),
                "review_count": user_reviews.count(),
                "favorite_count": profile.favorite_spots.count(),
            },
            "recent_activity": {
                "spots": [serialize_spot_summary(spot) for spot in user_spots[:3]],
                "reviews": [
                    serialize_review_activity(review) for review in user_reviews[:3]
                ],
            },
        }
    )


@csrf_exempt
@require_POST
def login_api(request):
    """JSONベースのログイン。"""

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return JsonResponse(
            {"success": False, "error": "ユーザー名とパスワードを入力してください。"},
            status=400,
        )

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse(
            {"success": False, "error": "ユーザー名またはパスワードが正しくありません。"},
            status=400,
        )

    login(request, user)
    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


@csrf_exempt
@require_POST
def logout_api(request):
    """ログアウトAPI。"""

    logout(request)
    response = JsonResponse({"success": True})
    response.delete_cookie("sessionid")
    return response


@csrf_exempt
@require_POST
def register_api(request):
    """ユーザー登録API。"""

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    form = UserCreationForm(payload)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "errors": form.errors},
            status=400,
        )

    user = form.save()
    messages.success(request, "アカウントが作成されました。")
    login(request, user)
    return JsonResponse(
        {
            "success": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
        }
    )


@csrf_exempt
@require_http_methods(["GET", "POST"])
def profile_api(request):
    """プロフィール情報の取得・更新。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "GET":
        return JsonResponse(
            {
                "profile": serialize_user_profile(profile),
                "user": {
                    "id": request.user.id,
                    "username": request.user.username,
                    "email": request.user.email,
                },
            }
        )

    form = UserProfileForm(request.POST, request.FILES, instance=profile)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "errors": form.errors},
            status=400,
        )
    form.save()
    return JsonResponse(
        {
            "success": True,
            "profile": serialize_user_profile(profile),
        }
    )


@csrf_exempt
@require_POST
def add_review_api(request, spot_id: int):
    """レビュー投稿API。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    spot = get_object_or_404(Spot, id=spot_id)

    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    form = ReviewForm(payload)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "errors": form.errors},
            status=400,
        )

    if Review.objects.filter(spot=spot, user=request.user).exists():
        return JsonResponse(
            {"success": False, "error": "既にレビューを投稿しています。"},
            status=400,
        )

    review = form.save(commit=False)
    review.spot = spot
    review.user = request.user
    review.save()

    return JsonResponse(
        {
            "success": True,
            "review": serialize_review(review),
        }
    )


@csrf_exempt
@require_POST
def toggle_favorite_api(request, spot_id: int):
    """お気に入り状態をトグルするAPI。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    spot = get_object_or_404(Spot, id=spot_id)
    try:
        is_now_favorite = toggle_favorite_spot(spot, request.user)
    except ValueError:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=400,
        )

    return JsonResponse({"success": True, "is_favorite": is_now_favorite})


@csrf_exempt
@require_POST
def add_spot_via_api(request):
    """スポット投稿API (FormData対応)。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    form = SpotForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse(
            {"success": False, "errors": form.errors},
            status=400,
        )

    spot = form.save(user=request.user)
    return JsonResponse(
        {
            "success": True,
            "spot": serialize_spot_summary(spot),
        }
    )


@csrf_exempt
@require_POST
def record_view_api(request, spot_id: int):
    """滞在時間の記録API。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    spot = get_object_or_404(Spot, id=spot_id)
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        payload = {}

    duration_ms = float(payload.get("duration_ms", 0))
    update_view_duration(spot, request.user, timedelta(milliseconds=max(duration_ms, 0)))
    return JsonResponse({"success": True})


@require_GET
def my_spots_data(request):
    """自分の投稿一覧を返す。"""

    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "ログインが必要です。"},
            status=401,
        )

    spots = (
        Spot.objects.filter(created_by=request.user)
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    return JsonResponse(
        {
            "spots": [serialize_spot_summary(spot) for spot in spots],
        }
    )


@require_GET
def recent_spots(request):
    """地図表示向けの最近のスポットを返す。"""

    spots = (
        Spot.objects.all()
        .select_related("created_by")
        .prefetch_related("tags")
        .order_by("-created_at")[:50]
    )
    return JsonResponse(
        {
            "spots": [serialize_spot_summary(spot) for spot in spots],
        }
    )


@require_GET
def search_suggestions(request):
    """検索候補を返す。"""

    query = request.GET.get("q", "")
    if not query:
        return JsonResponse({"results": []})

    spots = (
        Spot.objects.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(address__icontains=query)
            | Q(tags__name__icontains=query)
        )
        .distinct()[:10]
    )
    return JsonResponse({"results": [serialize_spot_brief(spot) for spot in spots]})
