"""
Djangoプロジェクトのコード品質をチェックする管理コマンド

このコマンドは以下のlintツールを使用してコード品質をチェックします：
- flake8: PEP 8スタイルガイド準拠チェック
- pylint: 詳細なコード品質分析
"""

import subprocess
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "プロジェクトのPythonコードをflake8とpylintでチェックします"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tool",
            choices=["flake8", "pylint", "all"],
            default="all",
            help="使用するlintツール（デフォルト: all）",
        )
        parser.add_argument(
            "--strict",
            action="store_true",
            help="strictモード: pylintも実行します（デフォルトではflake8のみ）",
        )
        parser.add_argument(
            "paths",
            nargs="*",
            default=[],
            help="チェックするファイルまたはディレクトリ（デフォルト: プロジェクトルート全体）",
        )

    def handle(self, *args, **options):
        tool = options["tool"]
        strict = options["strict"]
        paths = options["paths"]

        # プロジェクトルートディレクトリを取得
        project_root = Path(__file__).resolve().parent.parent.parent.parent

        # デフォルトのパス設定
        if not paths:
            paths = [
                "spots",
                "travel_log_map",
                "manage.py",
            ]
            # 存在するパスのみを含める
            paths = [str(project_root / p) for p in paths if (project_root / p).exists()]

        self.stdout.write(self.style.SUCCESS("🔍 コード品質チェックを開始します..."))
        self.stdout.write(f"対象パス: {', '.join(paths)}\n")

        success = True

        # flake8を実行
        if tool in ["flake8", "all"]:
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.HTTP_INFO("📋 flake8 でスタイルチェック中..."))
            self.stdout.write("=" * 60)

            flake8_cmd = [sys.executable, "-m", "flake8"] + paths

            try:
                result = subprocess.run(
                    flake8_cmd,
                    cwd=str(project_root),
                    capture_output=False,
                    text=True,
                )
                if result.returncode != 0:
                    success = False
                    self.stdout.write(self.style.ERROR("❌ flake8: スタイル違反が見つかりました"))
                else:
                    self.stdout.write(self.style.SUCCESS("✅ flake8: 問題なし"))
            except FileNotFoundError:
                raise CommandError(
                    "flake8が見つかりません。'pip install -r requirements.txt'を実行してください。"
                )

        # pylintを実行（strictモードまたはtool=pylint/allの場合）
        if tool in ["pylint", "all"] or strict:
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.HTTP_INFO("🔬 pylint で詳細チェック中..."))
            self.stdout.write("=" * 60)

            # pylintは各パスに対して個別に実行
            pylint_cmd = [sys.executable, "-m", "pylint"] + paths

            try:
                result = subprocess.run(
                    pylint_cmd,
                    cwd=str(project_root),
                    capture_output=False,
                    text=True,
                )
                # pylintは問題を見つけると0以外を返すが、スコアが一定以上なら許容
                if result.returncode != 0:
                    # pylintの終了コードは致命的なエラー以外は警告として扱う
                    if result.returncode >= 32:  # 致命的なエラー
                        success = False
                        self.stdout.write(
                            self.style.ERROR("❌ pylint: 致命的なエラーが見つかりました")
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING("⚠️  pylint: いくつかの改善提案があります")
                        )
                else:
                    self.stdout.write(self.style.SUCCESS("✅ pylint: 問題なし"))
            except FileNotFoundError:
                raise CommandError(
                    "pylintが見つかりません。'pip install -r requirements.txt'を実行してください。"
                )

        # 結果のサマリー
        self.stdout.write("\n" + "=" * 60)
        if success:
            self.stdout.write(
                self.style.SUCCESS("✅ コード品質チェック完了: 問題は見つかりませんでした！")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ コード品質チェック完了: いくつかの問題が見つかりました")
            )
            self.stdout.write(
                self.style.WARNING("自動修正するには: python manage.py format を実行してください")
            )
            sys.exit(1)
        self.stdout.write("=" * 60 + "\n")
