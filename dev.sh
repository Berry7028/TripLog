#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON_BIN:-python}"

load_env() {
  for candidate in ".env.local" ".env"; do
    if [ -f "$candidate" ]; then
      set -a
      . "$candidate"
      set +a
      break
    fi
  done
}

show_menu() {
  clear
  cat <<'EOF'
╔════════════════════════════════════════╗
║         Django 開発用ツール             ║
╚════════════════════════════════════════╝

【セットアップ】
  1. 依存パッケージをインストール

【マイグレーション】
  2. マイグレーション一覧表示
  3. マイグレーション実行
  4. 新しいマイグレーションを作成
  5. 特定のアプリのマイグレーションを作成

【サーバー】
  6. 開発サーバーを起動

【ユーザー管理】
  7. 管理ユーザー（スーパーユーザー）を作成

【その他】
  8. Django shell を開く
  9. 静的ファイルを収集
 10. テストを実行
 11. システムチェック
 12. フィクスチャをロード
 13. 任意のコマンドを実行
  0. 終了

EOF
  printf "選択してください (0-13): "
}

run_command() {
  case "$1" in
    1)
      echo "▶ 依存パッケージをインストール中..."
      "$PYTHON_BIN" -m pip install -r requirements.txt
      ;;
    2)
      echo "▶ マイグレーション一覧を表示中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" showmigrations
      ;;
    3)
      echo "▶ マイグレーションを実行中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" migrate
      ;;
    4)
      echo "▶ マイグレーションを作成中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" makemigrations
      ;;
    5)
      printf "アプリ名を入力 (例: spots, accounts): "
      read -r app_name
      if [ -n "$app_name" ]; then
        echo "▶ $app_name のマイグレーションを作成中..."
        "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" makemigrations "$app_name"
      fi
      ;;
    6)
      addr="${ADDR_PORT:-127.0.0.1:8000}"
      echo "▶ 開発サーバーを起動中 ($addr)..."
      echo "   停止するには Ctrl+C を押してください"
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" runserver "$addr"
      ;;
    7)
      echo "▶ 管理ユーザーを作成中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" createsuperuser
      ;;
    8)
      echo "▶ Django shell を起動中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" shell
      ;;
    9)
      echo "▶ 静的ファイルを収集中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" collectstatic --no-input
      ;;
    10)
      echo "▶ テストを実行中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" test
      ;;
    11)
      echo "▶ システムチェックを実行中..."
      "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" check
      ;;
    12)
      printf "フィクスチャのパスを入力 (例: fixtures/sample.json): "
      read -r fixture_path
      if [ -n "$fixture_path" ]; then
        echo "▶ $fixture_path をロード中..."
        "$PYTHON_BIN" "$PROJECT_ROOT/manage.py" loaddata "$fixture_path"
      fi
      ;;
    13)
      printf "実行するコマンドを入力 (例: createsuperuser --noinput): "
      read -r cmd
      if [ -n "$cmd" ]; then
        echo "▶ コマンドを実行中: $cmd"
        $("$PYTHON_BIN" "$PROJECT_ROOT/manage.py" $cmd)
      fi
      ;;
    0)
      echo "終了します。"
      exit 0
      ;;
    *)
      echo "❌ 無効な選択です。"
      ;;
  esac
}

main() {
  load_env
  
  # コマンドライン引数がある場合はそのまま実行
  if [ $# -gt 0 ]; then
    run_command "$@"
    exit 0
  fi
  
  # インタラクティブモード
  while true; do
    show_menu
    read -r choice
    
    if [ -z "$choice" ]; then
      continue
    fi
    
    run_command "$choice"
    
    if [ "$choice" != "6" ] && [ "$choice" != "8" ] && [ "$choice" != "0" ]; then
      printf "\n▶ 任意のキーを押して続行..."
      read -r
    fi
  done
}

main "$@"
