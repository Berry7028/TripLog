from django import forms
from .models import Spot, Review, UserProfile


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
        fields = ['title', 'description', 'latitude', 'longitude', 'address', 'image']
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
        }


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
