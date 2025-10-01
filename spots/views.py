from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Avg, Count, F
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Spot, Review, UserProfile, Tag, SpotView, UserSpotInteraction, UserRecommendationScore
from .forms import SpotForm, ReviewForm, UserProfileForm


def home(request):
    """ホームページ - スポット一覧"""
    spots_qs = (
        Spot.objects.all()
        .select_related('created_by')
        .prefetch_related('reviews', 'tags')
    )

    # 検索機能
    # 空や未指定でもフォームに"None"が入らないよう空文字に正規化
    search_query = request.GET.get('search', '') or ''
    if search_query:
        spots_qs = spots_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    sort_mode = request.GET.get('sort', 'recent')
    if sort_mode not in ('recent', 'relevance'):
        sort_mode = 'recent'

    spots_list = list(spots_qs)
    recommendation_source = None
    recommendation_notice = None
    recommendation_scored_ids = []

    if sort_mode == 'relevance':
        if request.user.is_authenticated:
            # DBから保存済みスコアを取得して並び替え
            user_scores = UserRecommendationScore.objects.filter(
                user=request.user,
                spot__in=spots_list
            ).select_related('spot')
            
            if user_scores.exists():
                # スコアマップを作成
                score_map = {score.spot_id: score.score for score in user_scores}
                source_info = user_scores.first().source if user_scores.first() else 'none'
                
                # スコアがあるスポットとないスポットを分ける
                scored_spots = []
                unscored_spots = []
                
                for spot in spots_list:
                    if spot.id in score_map:
                        scored_spots.append(spot)
                        recommendation_scored_ids.append(spot.id)
                    else:
                        unscored_spots.append(spot)
                
                # スコアでソート
                scored_spots.sort(key=lambda s: score_map.get(s.id, 0), reverse=True)
                
                # スコアがあるスポットを先に、その後未スコアのスポットを追加
                spots_list = scored_spots + unscored_spots
                
                recommendation_source = source_info
                if source_info == 'api':
                    recommendation_notice = 'AIが分析したおすすめ順で表示しています。(beta)'
                elif source_info == 'fallback':
                    recommendation_notice = '閲覧履歴をもとに推定したおすすめ順です。'
                else:
                    recommendation_notice = 'おすすめ順で表示しています。'
            else:
                recommendation_notice = 'おすすめスコアがまだ計算されていません。しばらくお待ちください。'
        else:
            recommendation_notice = 'おすすめ順を利用するにはログインしてください。'

    # ページネーション
    paginator = Paginator(spots_list, 12)  # 1ページに12件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_mode': sort_mode,
        'recommendation_source': recommendation_source,
        'recommendation_notice': recommendation_notice,
        'recommendation_scored_ids': recommendation_scored_ids,
    }
    return render(request, 'spots/home.html', context)


def spot_detail(request, spot_id):
    """スポット詳細ページ"""
    spot = get_object_or_404(Spot, id=spot_id)
    # 閲覧ログを記録（GETアクセス時）
    if request.method == 'GET':
        try:
            SpotView.objects.create(spot=spot)
        except Exception:
            # ログ記録は失敗しても画面表示を継続
            pass
        if request.user.is_authenticated:
            try:
                interaction, created = UserSpotInteraction.objects.get_or_create(
                    user=request.user,
                    spot=spot,
                    defaults={'view_count': 1},
                )
                if not created:
                    interaction.view_count = F('view_count') + 1
                    interaction.save(update_fields=['view_count'])
                    interaction.refresh_from_db(fields=['view_count'])
            except Exception:
                # 記録に失敗しても画面表示を優先
                pass
    reviews = spot.reviews.all().select_related('user')

    # 平均評価を計算
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # シェアURL（絶対URL）
    share_url = request.build_absolute_uri(spot.get_absolute_url())

    # レビューフォーム
    review_form = None
    if request.user.is_authenticated:
        # 既にレビューしているかチェック
        existing_review = reviews.filter(user=request.user).first()
        if not existing_review:
            review_form = ReviewForm()
    
    # お気に入り状態を判定
    is_favorite = False
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            is_favorite = profile.favorite_spots.filter(id=spot.id).exists()
        except UserProfile.DoesNotExist:
            is_favorite = False

    context = {
        'spot': spot,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'is_favorite': is_favorite,
        'share_url': share_url,
    }
    return render(request, 'spots/spot_detail.html', context)


@login_required
@require_POST
def record_spot_view(request, spot_id):
    """スポット閲覧の滞在時間を記録"""

    spot = get_object_or_404(Spot, id=spot_id)

    try:
        duration_ms = float(request.POST.get('duration_ms', 0))
    except (TypeError, ValueError):
        duration_ms = 0.0

    duration_ms = max(duration_ms, 0.0)
    duration = timedelta(milliseconds=duration_ms)

    interaction, _ = UserSpotInteraction.objects.get_or_create(
        user=request.user,
        spot=spot,
        defaults={'view_count': 1},
    )

    if duration > timedelta(0):
        interaction.total_view_duration += duration

    # auto_now=True のため last_viewed_at は save 時に更新される
    interaction.save(update_fields=['total_view_duration', 'last_viewed_at'])

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
        
        results = []
        for spot in spots:
            results.append({
                'id': spot.id,
                'title': spot.title,
                'address': spot.address,
                'latitude': spot.latitude,
                'longitude': spot.longitude,
            })
        
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
    spots = Spot.objects.all().select_related('created_by')
    filter_mode = (request.GET.get('filter') or '').lower()
    if request.user.is_authenticated and filter_mode in ('mine', 'others'):
        if filter_mode == 'mine':
            spots = spots.filter(created_by=request.user)
        elif filter_mode == 'others':
            spots = spots.exclude(created_by=request.user)
    
    spots_data = []
    for spot in spots:
        spots_data.append({
            'id': spot.id,
            'title': spot.title,
            'description': spot.description,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'address': spot.address,
            'image': (spot.image_src or None),
            'created_by': spot.created_by.username,
            'created_at': spot.created_at.isoformat(),
            'tags': [t.name for t in spot.tags.all()],
        })
    
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
    if request.method == 'POST':
        try:
            # フォームデータを取得
            title = request.POST.get('title')
            description = request.POST.get('description')
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            address = request.POST.get('address', '')
            image = request.FILES.get('image')
            image_url = (request.POST.get('image_url') or '').strip()
            
            # バリデーション
            if not title or not description:
                return JsonResponse({'success': False, 'error': 'タイトルと説明は必須です。'})
            
            # スポットを作成
            spot = Spot.objects.create(
                title=title,
                description=description,
                latitude=latitude,
                longitude=longitude,
                address=address,
                image=image,
                image_url=image_url or None,
                created_by=request.user
            )
            
            # レスポンスデータ
            spot_data = {
                'id': spot.id,
                'title': spot.title,
                'description': spot.description,
                'latitude': spot.latitude,
                'longitude': spot.longitude,
                'address': spot.address,
                'image': (spot.image_src or None),
                'created_by': spot.created_by.username,
                'created_at': spot.created_at.isoformat(),
            }
            
            return JsonResponse({'success': True, 'spot': spot_data})
            
        except ValueError as e:
            return JsonResponse({'success': False, 'error': '座標の形式が正しくありません。'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'POSTメソッドが必要です。'})


@login_required
def toggle_favorite(request, spot_id):
    """スポットのお気に入りをトグル"""
    spot = get_object_or_404(Spot, id=spot_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        if profile.favorite_spots.filter(id=spot.id).exists():
            profile.favorite_spots.remove(spot)
            messages.info(request, 'お気に入りを解除しました。')
        else:
            profile.favorite_spots.add(spot)
            messages.success(request, 'お気に入りに追加しました！')
    return redirect('spot_detail', spot_id=spot.id)


def plan_view(request):
    """プランページ - iframeで外部サイトを表示"""
    return render(request, 'spots/plan.html')
