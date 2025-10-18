# Django 5.2.6 によって 2025-09-30 12:48 に生成

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("spots", "0006_userspotinteraction"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RecommendationJobLog",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "executed_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="実行日時"),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[
                            ("api", "API"),
                            ("fallback", "フォールバック"),
                            ("none", "スコアなし"),
                        ],
                        default="none",
                        max_length=20,
                        verbose_name="スコア算出元",
                    ),
                ),
                (
                    "triggered_by",
                    models.CharField(
                        choices=[
                            ("auto", "スケジュール"),
                            ("admin", "管理画面"),
                            ("cli", "CLI"),
                            ("api", "API ツールコール"),
                        ],
                        default="auto",
                        max_length=20,
                        verbose_name="実行トリガー",
                    ),
                ),
                (
                    "scored_spot_ids",
                    models.JSONField(
                        blank=True,
                        default=list,
                        verbose_name="スコアリング対象スポットID",
                    ),
                ),
                (
                    "metadata",
                    models.JSONField(
                        blank=True, default=dict, verbose_name="追加メタ情報"
                    ),
                ),
            ],
            options={
                "verbose_name": "おすすめ解析ログ",
                "verbose_name_plural": "おすすめ解析ログ",
                "ordering": ["-executed_at"],
            },
        ),
        migrations.CreateModel(
            name="RecommendationJobSetting",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "interval_hours",
                    models.PositiveIntegerField(
                        default=31,
                        help_text="バックグラウンド解析を実行する間隔 (例: 31 時間ごと)。",
                        validators=[django.core.validators.MinValueValidator(1)],
                        verbose_name="解析間隔 (時間)",
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True, verbose_name="バックグラウンド解析を有効化"
                    ),
                ),
                (
                    "last_run_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="最後に実行した日時"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="作成日時"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新日時"),
                ),
            ],
            options={
                "verbose_name": "おすすめ解析設定",
                "verbose_name_plural": "おすすめ解析設定",
            },
        ),
        migrations.RenameIndex(
            model_name="userspotinteraction",
            new_name="spots_users_user_id_54df8f_idx",
            old_name="spots_users_user_id_172c6c_idx",
        ),
        migrations.RenameIndex(
            model_name="userspotinteraction",
            new_name="spots_users_last_vi_e92b74_idx",
            old_name="spots_users_last_vi_4d8267_idx",
        ),
        migrations.AddField(
            model_name="recommendationjoblog",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="recommendation_logs",
                to=settings.AUTH_USER_MODEL,
                verbose_name="対象ユーザー",
            ),
        ),
        migrations.AddIndex(
            model_name="recommendationjoblog",
            index=models.Index(
                fields=["executed_at"], name="spots_recom_execute_ac7f81_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="recommendationjoblog",
            index=models.Index(
                fields=["user", "executed_at"], name="spots_recom_user_id_bb37b2_idx"
            ),
        ),
    ]
