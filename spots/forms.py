from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User

from .models import Spot, Review, UserProfile, Tag


def _normalize_tags(tags_text: str) -> list[str]:
    """カンマ区切りのタグ文字列を正規化し、一意なリストに変換する。"""
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
    """スポット投稿フォーム"""
    # カンマ区切りでタグを入力（任意）
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
        super().__init__(*args, **kwargs)
        instance: Spot | None = kwargs.get('instance')
        if instance and instance.pk:
            current_tags = instance.tags.values_list('name', flat=True)
            self.fields['tags_text'].initial = ', '.join(current_tags)

    def clean_tags_text(self):
        tags_text = self.cleaned_data.get('tags_text', '')
        try:
            _normalize_tags(tags_text)
        except forms.ValidationError as exc:
            raise exc
        return tags_text

    def save(self, commit=True, user=None):  # type: ignore[override]
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
        if hasattr(self, '_pending_instance'):
            self._apply_tags(self._pending_instance)
            delattr(self, '_pending_instance')

    def _apply_tags(self, instance: Spot):
        tags_text = self.cleaned_data.get('tags_text', '')
        tag_names = _normalize_tags(tags_text)
        tag_objs = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        instance.tags.set(tag_objs)

class ReviewForm(forms.ModelForm):
    """レビュー投稿フォーム"""
    
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
    """ユーザープロフィールフォーム"""
    
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
    """管理画面向けスポットフォーム（投稿者やAI生成フラグも編集可能）。"""

    class Meta(SpotForm.Meta):
        fields = [
            'title',
            'description',
            'latitude',
            'longitude',
            'address',
            'image',
            'image_url',
            'is_ai_generated',
            'created_by',
        ]
        widgets = {
            **SpotForm.Meta.widgets,
            'created_by': forms.Select(attrs={'class': 'form-select'}),
            'is_ai_generated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['created_by'].queryset = User.objects.order_by('username')
        self.fields['created_by'].label = '投稿者'
        self.fields['is_ai_generated'].label = 'AI生成'


class ReviewAdminForm(forms.ModelForm):
    """管理画面向けレビュー編集フォーム"""

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
    """タグ管理フォーム"""

    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'タグ名'}),
        }


class UserAdminForm(forms.ModelForm):
    """ユーザー管理フォーム"""

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
    """ユーザープロフィール管理フォーム"""

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'favorite_spots']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'favorite_spots': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 8}),
        }


class UserAdminCreateForm(UserCreationForm):
    """管理画面向けのユーザー新規作成フォーム"""

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
    """グループ管理フォーム"""

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
