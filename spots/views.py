from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

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
from .services.serializers import serialize_spot_brief, serialize_spot_summary


def home(request):
    """ホームページ - スポット一覧"""
    result = fetch_homepage_spots(
        user=request.user,
        search_query=request.GET.get('search', ''),
        sort_mode=request.GET.get('sort', 'recent'),
    )

    paginator = Paginator(result.spots, 12)  # 1ページに12件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': result.search_query,
        'sort_mode': result.sort_mode,
    }
    return render(request, 'spots/home.html', context)


def spot_detail(request, spot_id):
    """スポット詳細ページ"""
    spot = get_object_or_404(Spot, id=spot_id)
    if request.method == 'GET':
        log_spot_view(spot, request.user)
    reviews = spot.reviews.all().select_related('user')

    # 平均評価を計算
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # シェアURL（絶対URL）
    share_url = request.build_absolute_uri(spot.get_absolute_url())

    review_form = _build_review_form(request.user, reviews)

    # お気に入り状態を判定
    is_favorite = is_favorite_spot(spot, request.user)

    # 関連スポット（同じユーザーの投稿） - 現在のスポットを除いた最新5件のみ渡す
    related_spots = fetch_related_spots(spot)

    context = {
        'spot': spot,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'is_favorite': is_favorite,
        'share_url': share_url,
        'related_spots': related_spots,
    }

    return render(request, 'spots/spot_detail.html', context)


@login_required
@require_POST
def record_spot_view(request, spot_id):
    """スポット閲覧の滞在時間を記録"""

    spot = get_object_or_404(Spot, id=spot_id)
    duration_ms = _safe_float(request.POST.get('duration_ms', 0))
    update_view_duration(spot, request.user, timedelta(milliseconds=duration_ms))

    return JsonResponse({'success': True})


def ranking(request):
    """直近7日間の閲覧数ランキング"""
    week_ago = timezone.now() - timedelta(days=7)
    # 直近7日の閲覧数で集計し、上位順にソート
    ranked_spots = (
        Spot.objects.all()
        .annotate(weekly_views=Count('spot_views', filter=Q(spot_views__viewed_at__gte=week_ago)))
        .filter(weekly_views__gt=0)
        .select_related('created_by')
        .prefetch_related('tags')
        .order_by('-weekly_views', '-created_at')
    )
    context = {
        'ranked_spots': ranked_spots[:7],  # トップ7のみ表示
        'week_ago': week_ago,
    }
    return render(request, 'spots/ranking.html', context)


@login_required
def add_spot(request):
    """スポット投稿ページ"""
    if request.method == 'POST':
        form = SpotForm(request.POST, request.FILES)
        if form.is_valid():
            spot = form.save(user=request.user)
            messages.success(request, 'スポットを投稿しました！')
            return redirect('spot_detail', spot_id=spot.id)
    else:
        form = SpotForm()
    
    return render(request, 'spots/add_spot.html', {'form': form})


@login_required
def add_review(request, spot_id):
    """レビュー投稿"""
    spot = get_object_or_404(Spot, id=spot_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # 既存のレビューをチェック
            existing_review = Review.objects.filter(spot=spot, user=request.user).first()
            if existing_review:
                messages.error(request, 'このスポットには既にレビューを投稿しています。')
            else:
                review = form.save(commit=False)
                review.spot = spot
                review.user = request.user
                review.save()
                messages.success(request, 'レビューを投稿しました！')
    
    return redirect('spot_detail', spot_id=spot_id)


@login_required
def my_spots(request):
    """マイページ - 自分の投稿一覧"""
    spots = Spot.objects.filter(created_by=request.user)
    
    # ページネーション
    paginator = Paginator(spots, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'spots/my_spots.html', {'page_obj': page_obj})


@login_required
def profile(request):
    """プロフィールページ"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'プロフィールを更新しました！')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'spots/profile.html', context)


def user_profile(request, username):
    """他ユーザーのプロフィール閲覧ページ"""
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)

    user_spots = (
        profile_user.spot_set.select_related('created_by')
        .prefetch_related('tags')
        .order_by('-created_at')
    )
    user_reviews = profile_user.review_set.select_related('spot').order_by('-created_at')
    favorite_spots = (
        profile.favorite_spots.select_related('created_by')
        .prefetch_related('tags')
        .order_by('-created_at')[:6]
    )

    context = {
        'profile_user': profile_user,
        'profile': profile,
        'spot_count': user_spots.count(),
        'review_count': user_reviews.count(),
        'favorite_count': profile.favorite_spots.count(),
        'recent_spots': user_spots[:6],
        'recent_reviews': user_reviews[:5],
        'recent_favorites': favorite_spots,
        'can_edit_profile': request.user.is_authenticated and request.user == profile_user,
    }
    return render(request, 'spots/user_profile.html', context)


def register(request):
    """ユーザー登録"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}さん、アカウントが作成されました！')
            # 自動ログイン
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def search_spots_api(request):
    """スポット検索API（Ajax用）"""
    query = request.GET.get('q', '')
    if query:
        spots = Spot.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:10]  # 最大10件

        results = [serialize_spot_brief(spot) for spot in spots]

        return JsonResponse({'results': results})

    return JsonResponse({'results': []})


def map_view(request):
    """マップページ"""
    recent_spots = Spot.objects.all().select_related('created_by')[:10]
    
    context = {
        'recent_spots': recent_spots,
    }
    return render(request, 'spots/map.html', context)


def spots_api(request):
    """スポット一覧API"""
    spots = (
        Spot.objects.all()
        .select_related('created_by')
        .prefetch_related('tags')
    )
    filter_mode = (request.GET.get('filter') or '').lower()
    if request.user.is_authenticated and filter_mode in ('mine', 'others'):
        if filter_mode == 'mine':
            spots = spots.filter(created_by=request.user)
        elif filter_mode == 'others':
            spots = spots.exclude(created_by=request.user)

    spots_list = list(spots)
    spots_data = [serialize_spot_summary(spot) for spot in spots_list]

    return JsonResponse({'spots': spots_data})


def logout_view(request):
    """ログアウト（GET許可）してリダイレクト"""
    logout(request)
    try:
        from django.conf import settings
        next_url = getattr(settings, 'LOGOUT_REDIRECT_URL', '/') or '/'
    except Exception:
        next_url = '/'
    return redirect(next_url)


@login_required
def add_spot_api(request):
    """スポット追加API"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POSTメソッドが必要です。'}, status=405)

    form = SpotForm(request.POST, request.FILES)
    if not form.is_valid():
        return JsonResponse(
            {'success': False, 'error': _extract_first_error_message(form)},
            status=400,
        )

    spot = form.save(user=request.user)
    return JsonResponse({'success': True, 'spot': serialize_spot_summary(spot)})


@login_required
def toggle_favorite(request, spot_id):
    """スポットのお気に入りをトグル"""
    spot = get_object_or_404(Spot, id=spot_id)
    if request.method == 'POST':
        is_now_favorite = toggle_favorite_spot(spot, request.user)
        if is_now_favorite:
            messages.success(request, 'お気に入りに追加しました！')
        else:
            messages.info(request, 'お気に入りを解除しました。')
    return redirect('spot_detail', spot_id=spot.id)


def plan_view(request):
    """プランページ - iframeで外部サイトを表示"""
    return render(request, 'spots/plan.html')


def _build_review_form(user, reviews):
    if not getattr(user, 'is_authenticated', False):
        return None
    if reviews.filter(user=user).exists():
        return None
    return ReviewForm()


def _safe_float(raw_value) -> float:
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return 0.0


def _extract_first_error_message(form: SpotForm) -> str:
    errors = form.errors
    if hasattr(errors, 'items'):
        for _field, messages in errors.items():
            if messages:
                return messages[0]
    non_field_errors = form.non_field_errors()
    if non_field_errors:
        return non_field_errors[0]
    return '入力内容を確認してください。'


def licenses(request):
    """ライセンス・謝辞ページ"""
    return render(request, 'spots/licenses.html')
