# Django 5.2.6 によって 2025-09-06 01:32 に生成

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Spot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='スポット名')),
                ('description', models.TextField(verbose_name='説明')),
                ('latitude', models.FloatField(verbose_name='緯度')),
                ('longitude', models.FloatField(verbose_name='経度')),
                ('address', models.CharField(blank=True, max_length=300, verbose_name='住所')),
                ('image', models.ImageField(blank=True, null=True, upload_to='spot_images/', verbose_name='画像')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新日時')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='投稿者')),
            ],
            options={
                'verbose_name': 'スポット',
                'verbose_name_plural': 'スポット',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, max_length=500, verbose_name='自己紹介')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='アバター')),
                ('favorite_spots', models.ManyToManyField(blank=True, to='spots.spot', verbose_name='お気に入りスポット')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='ユーザー')),
            ],
            options={
                'verbose_name': 'ユーザープロフィール',
                'verbose_name_plural': 'ユーザープロフィール',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], verbose_name='評価')),
                ('comment', models.TextField(verbose_name='コメント')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='レビュー者')),
                ('spot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='spots.spot', verbose_name='スポット')),
            ],
            options={
                'verbose_name': 'レビュー',
                'verbose_name_plural': 'レビュー',
                'ordering': ['-created_at'],
                'unique_together': {('spot', 'user')},
            },
        ),
    ]
