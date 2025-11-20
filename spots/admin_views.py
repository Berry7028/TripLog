"""
Custom admin dashboard views for staff users.

This module provides a set of views for a custom administrative interface,
allowing staff members to manage spots, users, reviews, and groups without
relying solely on the default Django Admin site.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Dict, List, Optional
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, Permission, User
from django.db.models import Avg, Count, Q
from django.http import HttpRequest, HttpResponse
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
from .models import Review, Spot, SpotView, Tag, UserProfile


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin to restrict view access to staff users only.

    Redirects non-staff users to the home page or login page.
    """

    login_url = 'login'

    def test_func(self) -> bool:
        """
        Checks if the current user has staff privileges.

        Returns:
            bool: True if user is staff, False otherwise.
        """
        return self.request.user.is_staff

    def handle_no_permission(self):
        """
        Handles requests from users without permission.

        Returns:
            HttpResponse: Redirect to home with an error message for authenticated users,
                          or redirects to login for anonymous users.
        """
        if self.request.user.is_authenticated:
            messages.error(self.request, '管理者権限が必要です。')
            return redirect('home')
        return super().handle_no_permission()


class AdminPermissionRequiredMixin(StaffRequiredMixin):
    """
    Mixin to require specific permissions for staff users.

    Extends StaffRequiredMixin to also check for specific Django permissions.
    Superusers are automatically granted access.
    """

    required_permissions: tuple[str, ...] = ()

    def get_required_permissions(self) -> tuple[str, ...]:
        """
        Returns the list of required permissions.

        Returns:
            tuple[str, ...]: Tuple of permission strings (e.g., 'auth.view_user').
        """
        return self.required_permissions

    def test_func(self) -> bool:
        """
        Checks if the user is staff and has all required permissions.

        Returns:
            bool: True if access is granted, False otherwise.
        """
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
    """
    Renders the main admin dashboard.

    Displays key metrics such as total counts of spots, reviews, users, and tags,
    as well as recent activity and top-ranking content.
    """

    template_name = 'spots/admin/dashboard.html'

    def get_context_data(self, **kwargs):
        """
        Populates the context with dashboard statistics.

        Returns:
            dict: Context data including various counts and querysets for the dashboard.
        """
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        context.update(
            {
                'total_spots': Spot.objects.count(),
                'total_reviews': Review.objects.count(),
                'total_users': User.objects.count(),
                'total_tags': Tag.objects.count(),
                'views_last_week': SpotView.objects.filter(viewed_at__gte=week_ago).count(),
                'new_spots': Spot.objects.select_related('created_by')
                .prefetch_related('tags')
                .order_by('-created_at')[:5],
                'recent_reviews': Review.objects.select_related('spot', 'user').order_by('-created_at')[:5],
                'top_spots': Spot.objects.annotate(
                    weekly_views=Count(
                        'spot_views',
                        filter=Q(spot_views__viewed_at__gte=week_ago),
                        distinct=True,
                    ),
                    review_avg=Avg('reviews__rating'),
                )
                .select_related('created_by')
                .order_by('-weekly_views', '-created_at')[:5],
                'popular_tags': Tag.objects.annotate(spot_count=Count('spots', distinct=True))
                .order_by('-spot_count', 'name')[:10],
                'top_reviewers': User.objects.annotate(review_count=Count('review', distinct=True))
                .filter(review_count__gt=0)
                .order_by('-review_count', 'username')[:5],
            }
        )
        return context


class SpotAdminListView(StaffRequiredMixin, ListView):
    """
    Displays a paginated list of spots for administration.

    Supports filtering by search query, tag, and creator.
    """
    template_name = 'spots/admin/spot_list.html'
    model = Spot
    context_object_name = 'spots'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Constructs the queryset for the spot list.

        Applies filters based on GET parameters and annotates with review counts
        and weekly view statistics.

        Returns:
            QuerySet: Filtered and ordered list of spots.
        """
        week_ago = timezone.now() - timedelta(days=7)
        queryset = (
            Spot.objects.select_related('created_by')
            .prefetch_related('tags')
            .annotate(
                review_count=Count('reviews', distinct=True),
                weekly_views=Count(
                    'spot_views',
                    filter=Q(spot_views__viewed_at__gte=week_ago),
                    distinct=True,
                ),
            )
        )
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(address__icontains=search)
                | Q(tags__name__icontains=search)
            ).distinct()
        tag_id = self.request.GET.get('tag')
        if tag_id:
            queryset = queryset.filter(tags__id=tag_id)
        creator_id = self.request.GET.get('creator')
        if creator_id:
            queryset = queryset.filter(created_by__id=creator_id)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        """
        Adds filter options (tags, creators) to the context.

        Returns:
            dict: Context data with filter options and current filter state.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'search_query': self.request.GET.get('q', '').strip(),
                'selected_tag': self.request.GET.get('tag', ''),
                'selected_creator': self.request.GET.get('creator', ''),
                'tags': Tag.objects.order_by('name'),
                'creators': User.objects.order_by('username'),
            }
        )
        return context


class SpotAdminCreateView(StaffRequiredMixin, CreateView):
    """
    View for creating a new spot via the admin interface.
    """
    model = Spot
    form_class = SpotAdminForm
    template_name = 'spots/admin/spot_form.html'
    success_url = reverse_lazy('admin_spot_list')

    def form_valid(self, form):
        """
        Handles successful form submission.

        Args:
            form (SpotAdminForm): The valid form.

        Returns:
            HttpResponse: Redirect to success URL with success message.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'スポットを作成しました。')
        return response

    def form_invalid(self, form):
        """
        Handles invalid form submission.

        Args:
            form (SpotAdminForm): The invalid form.

        Returns:
            HttpResponse: Re-renders the form with error messages.
        """
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class SpotAdminUpdateView(StaffRequiredMixin, UpdateView):
    """
    View for updating an existing spot via the admin interface.
    """
    model = Spot
    form_class = SpotAdminForm
    template_name = 'spots/admin/spot_form.html'
    success_url = reverse_lazy('admin_spot_list')

    def form_valid(self, form):
        """
        Handles successful form submission.

        Args:
            form (SpotAdminForm): The valid form.

        Returns:
            HttpResponse: Redirect to success URL with success message.
        """
        response = super().form_valid(form)
        messages.success(self.request, 'スポットを更新しました。')
        return response

    def form_invalid(self, form):
        """
        Handles invalid form submission.

        Args:
            form (SpotAdminForm): The invalid form.

        Returns:
            HttpResponse: Re-renders the form with error messages.
        """
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class SpotAdminDeleteView(StaffRequiredMixin, DeleteView):
    """
    View for deleting a spot via the admin interface.
    """
    model = Spot
    template_name = 'spots/admin/spot_confirm_delete.html'
    success_url = reverse_lazy('admin_spot_list')

    def delete(self, request, *args, **kwargs):
        """
        Executes the deletion and displays a success message.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: Redirect to success URL.
        """
        messages.success(request, 'スポットを削除しました。')
        return super().delete(request, *args, **kwargs)


class TagAdminListView(StaffRequiredMixin, ListView):
    """
    Displays a list of tags for administration.
    """
    template_name = 'spots/admin/tag_list.html'
    model = Tag
    context_object_name = 'tags'
    paginate_by = 30
    ordering = ['name']

    def get_queryset(self):
        """
        Returns a queryset of tags, filtered by search query.

        Annotates each tag with the count of associated spots.

        Returns:
            QuerySet: Filtered tag list.
        """
        queryset = Tag.objects.annotate(spot_count=Count('spots', distinct=True))
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Adds the search query to the context.

        Returns:
            dict: Context data.
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class TagAdminCreateView(StaffRequiredMixin, CreateView):
    """View for creating a new tag."""
    model = Tag
    form_class = TagForm
    template_name = 'spots/admin/tag_form.html'
    success_url = reverse_lazy('admin_tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'タグを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class TagAdminUpdateView(StaffRequiredMixin, UpdateView):
    """View for updating an existing tag."""
    model = Tag
    form_class = TagForm
    template_name = 'spots/admin/tag_form.html'
    success_url = reverse_lazy('admin_tag_list')

    def form_valid(self, form):
        messages.success(self.request, 'タグを更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class TagAdminDeleteView(StaffRequiredMixin, DeleteView):
    """View for deleting a tag."""
    model = Tag
    template_name = 'spots/admin/tag_confirm_delete.html'
    success_url = reverse_lazy('admin_tag_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'タグを削除しました。')
        return super().delete(request, *args, **kwargs)


class ReviewAdminListView(StaffRequiredMixin, ListView):
    """
    Displays a list of reviews for administration.
    """
    template_name = 'spots/admin/review_list.html'
    model = Review
    context_object_name = 'reviews'
    paginate_by = 25
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Returns a filtered list of reviews.

        Filters by search query (spot title, username, comment) and rating.

        Returns:
            QuerySet: Filtered review list.
        """
        queryset = Review.objects.select_related('spot', 'user').order_by('-created_at')
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(spot__title__icontains=search)
                | Q(user__username__icontains=search)
                | Q(comment__icontains=search)
            )
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'search_query': self.request.GET.get('q', '').strip(),
                'selected_rating': self.request.GET.get('rating', ''),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles bulk actions (e.g., deleting selected reviews).

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: Redirect to the review list.
        """
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected')
        if action == 'delete_selected' and selected_ids:
            deleted_count, _ = Review.objects.filter(pk__in=selected_ids).delete()
            messages.success(request, f'{deleted_count}件のレビューを削除しました。')
        else:
            messages.info(request, '操作対象が選択されていません。')
        return redirect('admin_review_list')


class ReviewAdminUpdateView(StaffRequiredMixin, UpdateView):
    """View for updating a review."""
    model = Review
    form_class = ReviewAdminForm
    template_name = 'spots/admin/review_form.html'
    success_url = reverse_lazy('admin_review_list')

    def form_valid(self, form):
        messages.success(self.request, 'レビューを更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class ReviewAdminCreateView(StaffRequiredMixin, CreateView):
    """View for creating a review."""
    model = Review
    form_class = ReviewAdminForm
    template_name = 'spots/admin/review_form.html'
    success_url = reverse_lazy('admin_review_list')

    def form_valid(self, form):
        messages.success(self.request, 'レビューを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class ReviewAdminDeleteView(StaffRequiredMixin, DeleteView):
    """View for deleting a review."""
    model = Review
    template_name = 'spots/admin/review_confirm_delete.html'
    success_url = reverse_lazy('admin_review_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'レビューを削除しました。')
        return super().delete(request, *args, **kwargs)


class UserAdminListView(AdminPermissionRequiredMixin, ListView):
    """
    Displays a list of users for administration.

    Requires specific permissions (auth.view_user) to access.
    """
    template_name = 'spots/admin/user_list.html'
    model = User
    context_object_name = 'users'
    paginate_by = 25
    ordering = ['username']
    required_permissions = ('auth.view_user',)

    def get_queryset(self):
        """
        Returns a filtered list of users.

        Filters by search query, staff status, and active status.

        Returns:
            QuerySet: Filtered user list.
        """
        queryset = User.objects.all()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        staff_filter = self.request.GET.get('staff')
        if staff_filter == '1':
            queryset = queryset.filter(is_staff=True)
        elif staff_filter == '0':
            queryset = queryset.filter(is_staff=False)
        active_filter = self.request.GET.get('active')
        if active_filter == '1':
            queryset = queryset.filter(is_active=True)
        elif active_filter == '0':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'search_query': self.request.GET.get('q', '').strip(),
                'selected_staff': self.request.GET.get('staff', ''),
                'selected_active': self.request.GET.get('active', ''),
            }
        )
        return context


class UserAdminCreateView(AdminPermissionRequiredMixin, CreateView):
    """
    View for creating a new user.

    Requires 'auth.add_user' permission.
    """
    model = User
    form_class = UserAdminCreateForm
    template_name = 'spots/admin/user_form.html'
    success_url = reverse_lazy('admin_user_list')
    required_permissions = ('auth.add_user',)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request_user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'ユーザーを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class UserAdminDetailView(AdminPermissionRequiredMixin, TemplateView):
    """
    View for displaying and editing user details and their profile.

    Requires 'auth.view_user' to view and 'auth.change_user' to edit.
    """
    template_name = 'spots/admin/user_detail.html'

    def get_required_permissions(self) -> tuple[str, ...]:
        """
        Dynamically sets required permissions based on request method.

        Returns:
            tuple[str, ...]: Permission strings.
        """
        if self.request.method.upper() == 'POST':
            return ('auth.change_user',)
        return ('auth.view_user',)

    def dispatch(self, request, *args, **kwargs):
        """
        Loads the target user object before processing the request.
        """
        self.user_obj = get_object_or_404(User, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Populates context with user data, forms, and recent activity.
        """
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.user_obj)
        context.update(
            {
                'user_obj': self.user_obj,
                'profile': profile,
                'user_form': kwargs.get('user_form')
                or UserAdminForm(instance=self.user_obj, request_user=self.request.user),
                'profile_form': kwargs.get('profile_form')
                or UserProfileAdminForm(instance=profile),
                'recent_spots': self.user_obj.spot_set.select_related('created_by').order_by('-created_at')[:5],
                'recent_reviews': self.user_obj.review_set.select_related('spot').order_by('-created_at')[:5],
                'available_permissions': Permission.objects.order_by('content_type__app_label', 'codename'),
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        """
        Handles updating the user and their profile.

        Args:
            request (HttpRequest): The HTTP request.

        Returns:
            HttpResponse: Redirect to the same page on success, or re-render with errors.
        """
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
            messages.success(request, 'ユーザー情報を更新しました。')
            return redirect('admin_user_detail', pk=self.user_obj.pk)
        messages.error(request, '入力内容を確認してください。')
        context = self.get_context_data(user_form=user_form, profile_form=profile_form)
        return self.render_to_response(context)


class UserAdminPasswordChangeView(AdminPermissionRequiredMixin, FormView):
    """
    View for changing a user's password.

    Requires 'auth.change_user' permission.
    """
    template_name = 'spots/admin/user_password.html'
    form_class = AdminPasswordChangeForm
    required_permissions = ('auth.change_user',)

    def dispatch(self, request, *args, **kwargs):
        self.user_obj = get_object_or_404(User, pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = self.form_class(user=self.user_obj, data=self.request.POST or None)
        for field in form.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        return form

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'パスワードを更新しました。')
        return redirect('admin_user_detail', pk=self.user_obj.pk)

    def form_invalid(self, form):
        messages.error(self.request, 'パスワードを更新できませんでした。')
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'user_obj': self.user_obj})
        return context


class GroupAdminListView(StaffRequiredMixin, ListView):
    """Displays a list of user groups."""
    template_name = 'spots/admin/group_list.html'
    model = Group
    context_object_name = 'groups'
    paginate_by = 25
    ordering = ['name']

    def get_queryset(self):
        queryset = Group.objects.all()
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class GroupAdminCreateView(StaffRequiredMixin, CreateView):
    """View for creating a new group."""
    model = Group
    form_class = GroupAdminForm
    template_name = 'spots/admin/group_form.html'
    success_url = reverse_lazy('admin_group_list')

    def form_valid(self, form):
        messages.success(self.request, 'グループを作成しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class GroupAdminUpdateView(StaffRequiredMixin, UpdateView):
    """View for updating an existing group."""
    model = Group
    form_class = GroupAdminForm
    template_name = 'spots/admin/group_form.html'
    success_url = reverse_lazy('admin_group_list')

    def form_valid(self, form):
        messages.success(self.request, 'グループを更新しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, '入力内容を確認してください。')
        return super().form_invalid(form)


class GroupAdminDeleteView(StaffRequiredMixin, DeleteView):
    """View for deleting a group."""
    model = Group
    template_name = 'spots/admin/group_confirm_delete.html'
    success_url = reverse_lazy('admin_group_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'グループを削除しました。')
        return super().delete(request, *args, **kwargs)


class UserProfileAdminListView(StaffRequiredMixin, ListView):
    """
    Displays a list of user profiles.
    """
    template_name = 'spots/admin/profile_list.html'
    model = UserProfile
    context_object_name = 'profiles'
    paginate_by = 25
    ordering = ['user__username']

    def get_queryset(self):
        """
        Returns a filtered list of user profiles.

        Filters by search query across username, bio, and favorite spot titles.

        Returns:
            QuerySet: Filtered profile list.
        """
        queryset = UserProfile.objects.select_related('user').prefetch_related('favorite_spots')
        search = self.request.GET.get('q', '').strip()
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search)
                | Q(bio__icontains=search)
                | Q(favorite_spots__title__icontains=search)
            ).distinct()
        return queryset.order_by('user__username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class SpotViewAdminListView(StaffRequiredMixin, ListView):
    """
    Displays a list of spot view logs.
    """
    template_name = 'spots/admin/spotview_list.html'
    model = SpotView
    context_object_name = 'logs'
    paginate_by = 50
    ordering = ['-viewed_at']

    def get_queryset(self):
        """
        Returns a filtered list of spot view logs.

        Filters by spot ID and date range.

        Returns:
            QuerySet: Filtered log list.
        """
        queryset = SpotView.objects.select_related('spot').order_by('-viewed_at')
        spot_id = self.request.GET.get('spot')
        if spot_id:
            queryset = queryset.filter(spot_id=spot_id)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(viewed_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(viewed_at__date__lte=date_to)
        return queryset

    def get_context_data(self, **kwargs):
        """
        Populates context with filter options.

        Returns:
            dict: Context data.
        """
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'spots': Spot.objects.order_by('title'),
                'selected_spot': self.request.GET.get('spot', ''),
                'date_from': self.request.GET.get('date_from', ''),
                'date_to': self.request.GET.get('date_to', ''),
            }
        )
        return context
