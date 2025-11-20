"""
Views for the TripLog application.

This module handles the HTTP requests and returns responses for the web interface,
including pages for home, spot details, user profile, and various API endpoints.
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
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


def home(request: HttpRequest) -> HttpResponse:
    """
    Renders the homepage with a list of spots.

    Handles search queries and sorting parameters from the request.
    Displays a paginated list of spots (12 per page).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered homepage template.
    """
    result = fetch_homepage_spots(
        user=request.user,
        search_query=request.GET.get('search', ''),
        sort_mode=request.GET.get('sort', 'recent'),
    )

    paginator = Paginator(result.spots, 12)  # 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': result.search_query,
        'sort_mode': result.sort_mode,
    }
    return render(request, 'spots/home.html', context)


def spot_detail(request: HttpRequest, spot_id: int) -> HttpResponse:
    """
    Renders the detailed view for a specific spot.

    - Logs the view event.
    - Calculates average rating.
    - Determines if the user has favorited the spot.
    - Fetches related spots by the same author.
    - Handles the display of the review form if the user hasn't reviewed yet.

    Args:
        request (HttpRequest): The HTTP request object.
        spot_id (int): The primary key of the spot to display.

    Returns:
        HttpResponse: The rendered spot detail template.
    """
    spot = get_object_or_404(Spot, id=spot_id)
    if request.method == 'GET':
        log_spot_view(spot, request.user)
    reviews = spot.reviews.all().select_related('user')

    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    # Absolute URL for sharing
    share_url = request.build_absolute_uri(spot.get_absolute_url())

    review_form = _build_review_form(request.user, reviews)

    # Check favorite status
    is_favorite = is_favorite_spot(spot, request.user)

    # Related spots (same author) - excluding current spot, latest 5
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
def record_spot_view(request: HttpRequest, spot_id: int) -> JsonResponse:
    """
    API endpoint to record the duration a user spent viewing a spot.

    Expected to be called via AJAX when a user leaves the page.

    Args:
        request (HttpRequest): The HTTP request object (POST only).
        spot_id (int): The ID of the spot.

    Returns:
        JsonResponse: A JSON response indicating success.
    """

    spot = get_object_or_404(Spot, id=spot_id)
    duration_ms = _safe_float(request.POST.get('duration_ms', 0))
    update_view_duration(spot, request.user, timedelta(milliseconds=duration_ms))

    return JsonResponse({'success': True})


def ranking(request: HttpRequest) -> HttpResponse:
    """
    Renders the ranking page showing the most viewed spots in the last 7 days.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered ranking template.
    """
    week_ago = timezone.now() - timedelta(days=7)
    # Aggregate by views in the last 7 days and sort descending
    ranked_spots = (
        Spot.objects.all()
        .annotate(weekly_views=Count('spot_views', filter=Q(spot_views__viewed_at__gte=week_ago)))
        .filter(weekly_views__gt=0)
        .select_related('created_by')
        .prefetch_related('tags')
        .order_by('-weekly_views', '-created_at')
    )
    context = {
        'ranked_spots': ranked_spots[:7],  # Top 7 only
        'week_ago': week_ago,
    }
    return render(request, 'spots/ranking.html', context)


@login_required
def add_spot(request: HttpRequest) -> HttpResponse:
    """
    Renders the page to create a new spot and handles form submission.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The add spot form or a redirect to the new spot's detail page.
    """
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
def add_review(request: HttpRequest, spot_id: int) -> HttpResponse:
    """
    Handles the submission of a new review for a spot.

    Args:
        request (HttpRequest): The HTTP request object.
        spot_id (int): The ID of the spot being reviewed.

    Returns:
        HttpResponse: A redirect to the spot detail page.
    """
    spot = get_object_or_404(Spot, id=spot_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check for existing review
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
def my_spots(request: HttpRequest) -> HttpResponse:
    """
    Renders the 'My Spots' page, listing spots created by the current user.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered my spots template.
    """
    spots = Spot.objects.filter(created_by=request.user)
    
    # Pagination
    paginator = Paginator(spots, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'spots/my_spots.html', {'page_obj': page_obj})


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    """
    Renders the user profile page and handles profile updates.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered profile template.
    """
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


def register(request: HttpRequest) -> HttpResponse:
    """
    Handles user registration.

    Displays the registration form and processes the creation of new user accounts.
    Logs the user in automatically upon successful registration.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The registration page or a redirect to home upon success.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}さん、アカウントが作成されました！')
            # Auto login
            user = authenticate(username=username, password=form.cleaned_data.get('password1'))
            if user:
                login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})


def search_spots_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint for searching spots (used for autocomplete/suggestions).

    Args:
        request (HttpRequest): The HTTP request object. Query param 'q' contains the search term.

    Returns:
        JsonResponse: A list of matching spots (max 10).
    """
    query = request.GET.get('q', '')
    if query:
        spots = Spot.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()[:10]  # Max 10 items

        results = [serialize_spot_brief(spot) for spot in spots]

        return JsonResponse({'results': results})

    return JsonResponse({'results': []})


def map_view(request: HttpRequest) -> HttpResponse:
    """
    Renders the main map view.

    Passes the 10 most recent spots to the template for initial display.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered map template.
    """
    recent_spots = Spot.objects.all().select_related('created_by')[:10]
    
    context = {
        'recent_spots': recent_spots,
    }
    return render(request, 'spots/map.html', context)


def spots_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to retrieve a list of spots.

    Supports filtering by 'mine' (current user's spots) or 'others' (other users' spots).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A dictionary containing the list of spots.
    """
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


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Logs out the user and redirects to the configured URL or homepage.

    Allows GET requests for logout (unlike standard Django which prefers POST).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: A redirect response.
    """
    logout(request)
    try:
        from django.conf import settings
        next_url = getattr(settings, 'LOGOUT_REDIRECT_URL', '/') or '/'
    except Exception:
        next_url = '/'
    return redirect(next_url)


@login_required
def add_spot_api(request: HttpRequest) -> JsonResponse:
    """
    API endpoint to create a new spot.

    Args:
        request (HttpRequest): The HTTP request object (POST only).

    Returns:
        JsonResponse: Success status and the created spot data, or error details.
    """
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
def toggle_favorite(request: HttpRequest, spot_id: int) -> HttpResponse:
    """
    Toggles the favorite status of a spot for the current user.

    Args:
        request (HttpRequest): The HTTP request object.
        spot_id (int): The ID of the spot to toggle.

    Returns:
        HttpResponse: A redirect back to the spot detail page.
    """
    spot = get_object_or_404(Spot, id=spot_id)
    if request.method == 'POST':
        is_now_favorite = toggle_favorite_spot(spot, request.user)
        if is_now_favorite:
            messages.success(request, 'お気に入りに追加しました！')
        else:
            messages.info(request, 'お気に入りを解除しました。')
    return redirect('spot_detail', spot_id=spot.id)


def plan_view(request: HttpRequest) -> HttpResponse:
    """
    Renders the plan page (currently a placeholder embedding an external site via iframe).

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered plan template.
    """
    return render(request, 'spots/plan.html')


def _build_review_form(user, reviews):
    """
    Helper to determine if a review form should be displayed.

    Returns:
        ReviewForm: An instance of ReviewForm if the user can review.
        None: If the user is anonymous or has already reviewed.
    """
    if not getattr(user, 'is_authenticated', False):
        return None
    if reviews.filter(user=user).exists():
        return None
    return ReviewForm()


def _safe_float(raw_value) -> float:
    """
    Safely converts a value to float.

    Args:
        raw_value: The value to convert.

    Returns:
        float: The converted float, or 0.0 if conversion fails.
    """
    try:
        return float(raw_value)
    except (TypeError, ValueError):
        return 0.0


def _extract_first_error_message(form: SpotForm) -> str:
    """
    Extracts the first available error message from a form.

    Args:
        form (SpotForm): The form with errors.

    Returns:
        str: The error message string.
    """
    errors = form.errors
    if hasattr(errors, 'items'):
        for _field, messages in errors.items():
            if messages:
                return messages[0]
    non_field_errors = form.non_field_errors()
    if non_field_errors:
        return non_field_errors[0]
    return '入力内容を確認してください。'
