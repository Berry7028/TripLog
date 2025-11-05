import json
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import RecommendationJobLog
from ...services import (
    build_recommendation_tool_context,
    build_recommendation_tool_schema,
    compute_and_store_all_user_scores,
    get_or_create_job_setting,
    is_job_due,
    run_recommendation_for_user,
    update_last_run,
)


class Command(BaseCommand):
    help = "AIおすすめ解析をバッチ実行し、全ユーザーのスコアをDBに保存します。"

    def add_arguments(self, parser):
        parser.add_argument("--user-id", type=int, help="特定ユーザーIDのみ解析する")
        parser.add_argument("--username", help="特定ユーザー名のみ解析する")
        parser.add_argument("--force", action="store_true", help="スケジュールを無視して実行する")
        parser.add_argument("--dry-run", action="store_true", help="ログ保存を行わず解析のみ行う")
        parser.add_argument(
            "--print-tool-schema",
            action="store_true",
            help="利用可能なツールコールのスキーマを表示する",
        )
        parser.add_argument(
            "--all-users",
            action="store_true",
            help="全ユーザーのスコアを計算してDBに保存する(デフォルト動作)",
        )

    def handle(self, *args, **options):
        if options["print_tool_schema"]:
            schema = build_recommendation_tool_schema()
            self.stdout.write(json.dumps(schema, ensure_ascii=False, indent=2))
            if not any(options.get(opt) for opt in ("user_id", "username", "force", "all_users")):
                return

        setting = get_or_create_job_setting()

        # 特定ユーザーの処理ではなく、全ユーザーの一括処理がデフォルト
        if not options["user_id"] and not options["username"]:
            # スケジュールチェック
            if not options["force"]:
                if not setting.enabled:
                    self.stdout.write(self.style.WARNING("おすすめ解析は無効化されています。"))
                    return
                if not is_job_due(setting):
                    self.stdout.write(
                        self.style.WARNING("設定された解析間隔に達していないためスキップします。")
                    )
                    return

            # 全ユーザーのスコアを計算して保存
            self.stdout.write("全ユーザーのおすすめスコアを計算中...")
            result = compute_and_store_all_user_scores(
                triggered_by=RecommendationJobLog.TRIGGER_AUTO,
            )

            if result["success"]:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 完了: {result["users_processed"]}ユーザー処理、'
                        f'{result["scores_saved"]}件のスコアを保存しました'
                    )
                )
                update_last_run(setting, now=timezone.now())
            else:
                self.stdout.write(
                    self.style.ERROR(f'一部エラーが発生しました: {len(result.get("errors", []))}件')
                )
                for error in result.get("errors", []):
                    self.stdout.write(self.style.WARNING(f"  - {error}"))

            return

        # 特定ユーザーの処理(既存のロジック)
        users = self._resolve_users(options)
        if not users:
            self.stdout.write(self.style.WARNING("解析対象となるユーザーが見つかりませんでした。"))
            return

        dry_run = options["dry_run"]
        triggered_by = RecommendationJobLog.TRIGGER_CLI

        processed = 0
        for user in users:
            result = run_recommendation_for_user(
                user,
                triggered_by=triggered_by,
                persist_log=not dry_run,
            )
            if result is None:
                self.stdout.write(
                    self.style.WARNING(f"{user.username}: 閲覧履歴がないためスキップしました。")
                )
                continue

            processed += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f"{user.username}: source={result.source} scored={len(result.scored_spot_ids)}"
                )
            )

            if dry_run:
                context = build_recommendation_tool_context(
                    user,
                    user.spot_interactions.select_related("spot").prefetch_related("spot__tags"),
                )
                preview_call = {
                    "user_id": user.id,
                    "username": user.username,
                    "source": result.source,
                    "schema_version": context["schema_version"],
                    "scores": [
                        {"spot_id": sid, "score": result.scores.get(sid, 0.0)}
                        for sid in sorted(result.scored_spot_ids)
                    ],
                }
                preview = StringIO()
                json.dump(preview_call, preview, ensure_ascii=False, indent=2)
                self.stdout.write("--- ツールコールプレビュー ---")
                self.stdout.write(preview.getvalue())

        if processed == 0:
            self.stdout.write(
                self.style.WARNING("解析は完了しましたが、保存対象はありませんでした。")
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"解析完了: {processed} ユーザーを処理しました。"))

    def _resolve_users(self, options):
        User = get_user_model()
        if options["user_id"] or options["username"]:
            filters = {}
            if options["user_id"]:
                filters["id"] = options["user_id"]
            if options["username"]:
                filters["username"] = options["username"]
            user = User.objects.filter(**filters).first()
            return [user] if user else []

        return list(User.objects.filter(spot_interactions__isnull=False).distinct().order_by("id"))
