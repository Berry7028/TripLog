from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Spot, Review, UserProfile
from .forms import SpotForm, ReviewForm, UserProfileForm


def home(request):
    """ホームページ - スポット一覧"""
    spots = Spot.objects.all().select_related('created_by').prefetch_related('reviews')
    
    # 検索機能
    search_query = request.GET.get('search')
    if search_query:
        spots = spots.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # ページネーション
    paginator = Paginator(spots, 12)  # 1ページに12件表示
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'spots/home.html', context)


def spot_detail(request, spot_id):
    """スポット詳細ページ"""
    spot = get_object_or_404(Spot, id=spot_id)
    reviews = spot.reviews.all().select_related('user')
    
    # 平均評価を計算
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    # レビューフォーム
    review_form = None
    if request.user.is_authenticated:
        # 既にレビューしているかチェック
        existing_review = reviews.filter(user=request.user).first()
        if not existing_review:
            review_form = ReviewForm()
    
    context = {
        'spot': spot,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
    }
    return render(request, 'spots/spot_detail.html', context)


@login_required
def add_spot(request):
    """スポット投稿ページ"""
    if request.method == 'POST':
        form = SpotForm(request.POST, request.FILES)
        if form.is_valid():
            spot = form.save(commit=False)
            spot.created_by = request.user
            spot.save()
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
            Q(address__icontains=query)
        )[:10]  # 最大10件
        
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
    
    spots_data = []
    for spot in spots:
        spots_data.append({
            'id': spot.id,
            'title': spot.title,
            'description': spot.description,
            'latitude': spot.latitude,
            'longitude': spot.longitude,
            'address': spot.address,
            'image': spot.image.url if spot.image else None,
            'created_by': spot.created_by.username,
            'created_at': spot.created_at.isoformat(),
        })
    
    return JsonResponse({'spots': spots_data})


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
                'image': spot.image.url if spot.image else None,
                'created_by': spot.created_by.username,
                'created_at': spot.created_at.isoformat(),
            }
            
            return JsonResponse({'success': True, 'spot': spot_data})
            
        except ValueError as e:
            return JsonResponse({'success': False, 'error': '座標の形式が正しくありません。'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'POSTメソッドが必要です。'})

