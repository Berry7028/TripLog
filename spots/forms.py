"""
Forms for the TripLog application.

This module defines the forms used for creating and updating Spots, Reviews,
UserProfiles, and various admin-specific forms for managing users and groups.
"""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User

from .models import Spot, Review, UserProfile, Tag


def _normalize_tags(tags_text: str) -> list[str]:
    """
    Normalizes a comma-separated string of tags into a unique list.

    Splits the input string by commas, strips whitespace, and removes duplicates
    and empty strings. Validates that each tag is within the character limit.

    Args:
        tags_text (str): The raw string of tags (e.g., "Sea, Mountain, View").

    Returns:
        list[str]: A list of unique tag names.

    Raises:
        forms.ValidationError: If any tag exceeds 50 characters.
    """
    seen = set()
    tags: list[str] = []
    for raw in (tags_text or '').split(','):
        name = raw.strip()
        if not name:
            continue
        if len(name) > 50:
            raise forms.ValidationError('タグは50文字以内で入力してください。')
        if name not in seen:
            seen.add(name)
            tags.append(name)
    return tags


class SpotForm(forms.ModelForm):
    """
    Form for creating or updating a Spot.

    Includes a custom field `tags_text` to handle comma-separated tag input.
    """

    # Input for tags as a comma-separated string (optional)
    tags_text = forms.CharField(
        required=False,
        label='タグ',
        help_text='カンマ区切りで入力（例: 海, 山, 絶景）',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '例: 海, 山, 絶景'
        })
    )

    class Meta:
        model = Spot
        fields = ['title', 'description', 'latitude', 'longitude', 'address', 'image', 'image_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'スポット名を入力してください'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'スポットの説明を入力してください'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': '緯度（例: 35.6762）'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any',
                'placeholder': '経度（例: 139.6503）'
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '住所を入力してください'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Initializes the form.

        If editing an existing instance, populates the `tags_text` field with
        the currently associated tags.
        """
        super().__init__(*args, **kwargs)
        instance: Spot | None = kwargs.get('instance')
        if instance and instance.pk:
            current_tags = instance.tags.values_list('name', flat=True)
            self.fields['tags_text'].initial = ', '.join(current_tags)

    def clean_tags_text(self):
        """
        Validates the tags_text field.

        Returns:
            str: The cleaned tags text.

        Raises:
            forms.ValidationError: If validation fails in `_normalize_tags`.
        """
        tags_text = self.cleaned_data.get('tags_text', '')
        try:
            _normalize_tags(tags_text)
        except forms.ValidationError as exc:
            raise exc
        return tags_text

    def save(self, commit=True, user=None):  # type: ignore[override]
        """
        Saves the form data to the database.

        Args:
            commit (bool): If True, save to the database immediately.
            user (User, optional): The user creating the spot. Required for new spots.

        Returns:
            Spot: The saved spot instance.
        """
        instance: Spot = super().save(commit=False)
        if user and not instance.pk:
            instance.created_by = user
        if commit:
            instance.save()
            self._apply_tags(instance)
        else:
            self._pending_instance = instance
        return instance

    def save_m2m(self):  # type: ignore[override]
        """
        Saves the many-to-many relationships (tags).

        Called automatically by Django when `save(commit=False)` is used followed by `form.save_m2m()`.
        """
        if hasattr(self, '_pending_instance'):
            self._apply_tags(self._pending_instance)
            delattr(self, '_pending_instance')

    def _apply_tags(self, instance: Spot):
        """
        Helper method to process and associate tags with the spot instance.
        """
        tags_text = self.cleaned_data.get('tags_text', '')
        tag_names = _normalize_tags(tags_text)
        tag_objs = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        instance.tags.set(tag_objs)


class ReviewForm(forms.ModelForm):
    """Form for users to submit a review for a spot."""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                choices=[(i, f'{i}★') for i in range(1, 6)],
                attrs={'class': 'form-control'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'レビューを入力してください'
            }),
        }


class UserProfileForm(forms.ModelForm):
    """Form for users to update their profile information."""
    
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '自己紹介を入力してください'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


class SpotAdminForm(SpotForm):
    """
    Admin-specific form for managing spots.

    Allows editing the creator of the spot in addition to standard fields.
    """

    class Meta(SpotForm.Meta):
        fields = [
            'title',
            'description',
            'latitude',
            'longitude',
            'address',
            'image',
            'image_url',
            'created_by',
        ]
        widgets = {
            **SpotForm.Meta.widgets,
            'created_by': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.order_by('username')
        self.fields['created_by'].label = '投稿者'


class ReviewAdminForm(forms.ModelForm):
    """Admin form for managing reviews."""

    class Meta:
        model = Review
        fields = ['spot', 'user', 'rating', 'comment']
        widgets = {
            'spot': forms.Select(attrs={'class': 'form-select'}),
            'user': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.Select(
                choices=[(i, f'{i}★') for i in range(1, 6)],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class TagForm(forms.ModelForm):
    """Form for managing tags."""

    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タグ名'}),
        }


class UserAdminForm(forms.ModelForm):
    """
    Admin form for updating existing users.

    Filters privileged fields for non-superuser admins.
    """

    privileged_fields = (
        'is_staff',
        'is_superuser',
        'groups',
        'user_permissions',
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
            'user_permissions': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
        }

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request_user is not None and not request_user.is_superuser:
            for field_name in self.privileged_fields:
                self.fields.pop(field_name, None)
        if 'groups' in self.fields:
            self.fields['groups'].queryset = Group.objects.order_by('name')
            self.fields['groups'].label = '所属グループ'
        if 'user_permissions' in self.fields:
            self.fields['user_permissions'].queryset = Permission.objects.order_by('content_type__app_label', 'codename')
            self.fields['user_permissions'].label = '個別パーミッション'


class UserProfileAdminForm(forms.ModelForm):
    """Admin form for managing user profiles."""

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'favorite_spots']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'favorite_spots': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
        }


class UserAdminCreateForm(UserCreationForm):
    """
    Admin form for creating new users.

    Extends the standard UserCreationForm to include admin-specific fields
    and styling.
    """

    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='有効')
    is_staff = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='スタッフ')
    is_superuser = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}), label='スーパーユーザー')
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 6}),
        label='所属グループ'
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
        label='個別パーミッション'
    )

    class Meta(UserCreationForm.Meta):
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions',
        )

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request_user is not None and not request_user.is_superuser:
            for field_name in UserAdminForm.privileged_fields:
                self.fields.pop(field_name, None)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        if 'groups' in self.fields:
            self.fields['groups'].queryset = Group.objects.order_by('name')
        if 'user_permissions' in self.fields:
            self.fields['user_permissions'].queryset = Permission.objects.order_by('content_type__app_label', 'codename')

    def save(self, commit=True):
        """
        Saves the new user with the extended fields.
        """
        user: User = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        user.is_active = self.cleaned_data.get('is_active', True)
        user.is_staff = self.cleaned_data.get('is_staff', False)
        user.is_superuser = self.cleaned_data.get('is_superuser', False)
        if commit:
            user.save()
            self.save_m2m()
        return user


class GroupAdminForm(forms.ModelForm):
    """Admin form for managing groups."""

    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'グループ名'}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 12}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.order_by('content_type__app_label', 'codename')
