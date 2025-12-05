from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group, Permission, User

from spots.models import Spot, Review, UserProfile, Tag
from spots.forms import SpotForm


class SpotAdminForm(SpotForm):
    """管理画面向けスポットフォーム（投稿者も編集可能）。"""

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
