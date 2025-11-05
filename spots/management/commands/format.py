"""
Djangoプロジェクトのコードをフォーマットする管理コマンド

このコマンドは以下のツールを使用してコードを自動フォーマットします：
- black: Pythonコードフォーマッター
- isort: import文の整理
"""

import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "プロジェクトのPythonコードをblackとisortでフォーマットします"

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="フォーマットせずに、変更が必要かどうかをチェックするのみ",
        )
        parser.add_argument(
            "paths",
            nargs="*",
            default=[],
            help="フォーマットするファイルまたはディレクトリ（デフォルト: プロジェクトルート全体）",
        )

    def handle(self, *args, **options):
        check_only = options["check"]
        paths = options["paths"]

        # プロジェクトルートディレクトリを取得
        project_root = Path(__file__).resolve().parent.parent.parent.parent

        # デフォルトのパス設定（プロジェクトの主要なディレクトリ）
        if not paths:
            paths = [
                "spots",
                "travel_log_map",
                "manage.py",
            ]
            # 存在するパスのみを含める
            paths = [str(project_root / p) for p in paths if (project_root / p).exists()]

        if check_only:
            self.stdout.write(self.style.WARNING("🔍 チェックモード: 変更は適用されません"))
        else:
            self.stdout.write(self.style.SUCCESS("🔧 コードフォーマットを開始します..."))

        success = True

        # isortを実行
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.HTTP_INFO("📦 isort でimport文を整理中..."))
        self.stdout.write("=" * 60)

        isort_cmd = [sys.executable, "-m", "isort"]
        if check_only:
            isort_cmd.append("--check-only")
        isort_cmd.extend(paths)

        try:
            result = subprocess.run(
                isort_cmd,
                cwd=str(project_root),
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                success = False
                if check_only:
                    self.stdout.write(
                        self.style.WARNING("⚠️  isort: フォーマットが必要なファイルがあります")
                    )
                else:
                    self.stdout.write(self.style.ERROR("❌ isort の実行に失敗しました"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ isort 完了"))
        except FileNotFoundError:
            raise CommandError(
                "isortが見つかりません。'pip install -r requirements.txt'を実行してください。"
            )

        # blackを実行
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.HTTP_INFO("🎨 black でコードをフォーマット中..."))
        self.stdout.write("=" * 60)

        black_cmd = [sys.executable, "-m", "black"]
        if check_only:
            black_cmd.append("--check")
        black_cmd.extend(paths)

        try:
            result = subprocess.run(
                black_cmd,
                cwd=str(project_root),
                capture_output=False,
                text=True,
            )
            if result.returncode != 0:
                success = False
                if check_only:
                    self.stdout.write(
                        self.style.WARNING("⚠️  black: フォーマットが必要なファイルがあります")
                    )
                else:
                    self.stdout.write(self.style.ERROR("❌ black の実行に失敗しました"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ black 完了"))
        except FileNotFoundError:
            raise CommandError(
                "blackが見つかりません。'pip install -r requirements.txt'を実行してください。"
            )

        # 結果のサマリー
        self.stdout.write("\n" + "=" * 60)
        if success:
            if check_only:
                self.stdout.write(
                    self.style.SUCCESS("✅ すべてのファイルが正しくフォーマットされています！")
                )
            else:
                self.stdout.write(self.style.SUCCESS("✅ フォーマットが完了しました！"))
        else:
            if check_only:
                self.stdout.write(self.style.ERROR("❌ フォーマットが必要なファイルがあります。"))
                self.stdout.write(
                    self.style.WARNING("修正するには: python manage.py format (--check なしで実行)")
                )
            else:
                self.stdout.write(self.style.ERROR("❌ フォーマット中にエラーが発生しました"))
            sys.exit(1)
        self.stdout.write("=" * 60 + "\n")
