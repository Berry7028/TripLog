#!/bin/bash

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPTS_DIR="$ROOT_DIR/scripts"
PROJECT_NAME="TripLog"

# =========================
# 出力フォーマット用ユーティリティ
# =========================
print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_warning() {
    echo -e "\033[33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

print_header() {
    echo -e "\n\033[36m🚀 $1\033[0m"
}

indent_output() {
    sed 's/^/   /'
}

# =========================
# Python / Django 判定ヘルパー
# =========================
resolve_python() {
    if [ -x "$ROOT_DIR/venv/bin/python" ]; then
        echo "$ROOT_DIR/venv/bin/python"
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        command -v python
        return 0
    fi

    return 1
}

run_manage_py() {
    local python_cmd
    python_cmd=$(resolve_python) || return 1
    (cd "$ROOT_DIR" && "$python_cmd" manage.py "$@")
}

# =========================
# 情報表示
# =========================
show_git_summary() {
    if ! command -v git >/dev/null 2>&1; then
        print_warning "Gitがインストールされていないため状態を取得できません"
        return
    fi

    local branch status
    branch=$(git -C "$ROOT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "不明")
    print_info "Gitブランチ: $branch"

    if status=$(git -C "$ROOT_DIR" status -sb 2>/dev/null); then
        echo "$status" | sed '1d' | indent_output
    else
        print_warning "Gitステータスを取得できませんでした"
    fi
}

show_python_summary() {
    if [ -x "$ROOT_DIR/venv/bin/python" ]; then
        local venv_python="$ROOT_DIR/venv/bin/python"
        print_info "venv Python: $($venv_python --version 2>&1)"
        if pip_info=$($venv_python -m pip --version 2>&1); then
            echo "$pip_info" | indent_output
        fi
    else
        print_warning "venv/ が見つからないため仮想環境が未作成の可能性があります"
    fi

    if command -v python3 >/dev/null 2>&1; then
        print_info "システム Python: $(python3 --version 2>&1)"
    fi
}

show_django_summary() {
    if [ ! -f "$ROOT_DIR/manage.py" ]; then
        print_warning "manage.py が存在しないためDjango情報を取得できません"
        return
    fi

    if ! python_cmd=$(resolve_python); then
        print_warning "Pythonが見つからないためDjango情報を取得できません"
        return
    fi

    if django_version=$(cd "$ROOT_DIR" && "$python_cmd" manage.py --version 2>/dev/null); then
        print_info "Djangoバージョン: $django_version"
    else
        print_warning "Djangoが未インストールの可能性があります (manage.py --version に失敗)"
        return
    fi

    if migrations=$(run_manage_py showmigrations --plan 2>/dev/null); then
        local pending applied total
        pending=$(echo "$migrations" | grep -c '^\s*\[ \]' || true)
        applied=$(echo "$migrations" | grep -c '^\s*\[X\]' || true)
        total=$((pending + applied))
        print_info "マイグレーション: ${applied}/${total} 適用済み (未適用: ${pending})"
        echo "🗂️  マイグレーション状況:"
        echo "$migrations" | indent_output
    else
        print_warning "マイグレーション状況を取得できませんでした (依存パッケージ未インストールの可能性)"
    fi
}

print_script_status() {
    local relative_path="$1"
    local description="$2"
    local target="$SCRIPTS_DIR/$relative_path"

    if [ -f "$target" ]; then
        if [[ "$relative_path" == *.py ]] || [ -x "$target" ]; then
            printf "   ✅ %-25s %s\n" "$relative_path" "$description"
        else
            printf "   ⚠️  %-25s %s (実行権限なし)\n" "$relative_path" "$description"
        fi
    else
        printf "   ❌ %-25s %s (ファイル未検出)\n" "$relative_path" "$description"
    fi
}

show_script_summary() {
    print_header "利用可能なスクリプト"

    print_script_status "dev_start.sh" "仮想環境構築と初期セットアップ"
    print_script_status "start_server.sh" "既存環境でのサーバー起動"
    print_script_status "ai_generate_spots.sh" "AIによるスポットデータ生成"
    print_script_status "flow/generate_flow.py" "画面フロー図の生成"
    print_script_status "run_recommendation_jobs.sh" "AI閲覧分析バッチの実行"
    print_script_status "run_tests.sh" "Djangoテストスイートの実行"
}

show_overview() {
    print_header "$PROJECT_NAME 開発ハブ"
    print_info "プロジェクトルート: $ROOT_DIR"
    show_git_summary
    show_python_summary
    show_django_summary
    show_script_summary
}

# =========================
# アクション
# =========================
run_dev_start() {
    print_header "開発セットアップを開始します"
    bash "$SCRIPTS_DIR/dev_start.sh"
}

run_start_server() {
    print_header "Django開発サーバーを起動します"
    bash "$SCRIPTS_DIR/start_server.sh"
}

run_ai_generator() {
    print_header "AIスポット生成スクリプトを起動します"
    bash "$SCRIPTS_DIR/ai_generate_spots.sh"
}

run_flow_generator() {
    local base_url
    read -r -p "ベースURLを入力してください (デフォルト: http://127.0.0.1:8000/): " base_url
    if [ -z "$base_url" ]; then
        base_url="http://127.0.0.1:8000/"
    fi

    if ! python_cmd=$(resolve_python); then
        print_error "Pythonが見つからないためフロージェネレーターを実行できません"
        return 1
    fi

    print_header "画面フロー図を生成します"
    (cd "$ROOT_DIR" && "$python_cmd" "$SCRIPTS_DIR/flow/generate_flow.py" --base-url "$base_url")
}

run_tests() {
    print_header "Djangoテストスイートを実行します"
    if ! run_manage_py test "$@"; then
        print_error "テストの実行に失敗しました"
        return 1
    fi
}

run_recommendation_job() {
    print_header "AIおすすめ解析ジョブを実行します"
    local user_input force_choice schema_choice
    declare -a args=()

    read -r -p "特定ユーザーIDを指定しますか？(空欄で全体解析): " user_input
    if [ -n "$user_input" ]; then
        args+=(--user-id "$user_input")
    fi

    read -r -p "force オプションで即時実行しますか？(y/N): " force_choice
    if [[ "$force_choice" =~ ^[Yy]$ ]]; then
        args+=(--force)
    fi

    read -r -p "ツールスキーマを表示しますか？(y/N): " schema_choice
    if [[ "$schema_choice" =~ ^[Yy]$ ]]; then
        args+=(--print-tool-schema)
    fi

    bash "$SCRIPTS_DIR/run_recommendation_jobs.sh" "${args[@]}"
}

run_tests_interactive() {
    local input
    read -r -p "manage.py test に渡す追加引数 (空欄で全テスト): " input
    if [ -z "$input" ]; then
        run_tests
    else
        IFS=' ' read -r -a extra_args <<< "$input"
        run_tests "${extra_args[@]}"
    fi
}

run_migrations() {
    print_header "マイグレーションを作成・適用します"
    if ! run_manage_py makemigrations; then
        print_error "makemigrations に失敗しました"
        return 1
    fi
    if ! run_manage_py migrate; then
        print_error "migrate に失敗しました"
        return 1
    fi
    print_info "マイグレーションが完了しました"
}

# =========================
# メニュー / CLI
# =========================
show_menu() {
    while true; do
        show_overview
        cat <<'MENU'

選択肢を入力してください:
  1) 情報を再表示
  2) 開発セットアップ (dev_start.sh)
  3) サーバー起動 (start_server.sh)
  4) AIスポット生成 (ai_generate_spots.sh)
  5) 画面フロー図生成 (flow/generate_flow.py)
  6) テスト実行 (manage.py test)
  7) requirements.txt インストール (pip install -r requirements.txt)
  8) マイグレーション実行 (makemigrations && migrate)
  9) AI閲覧分析バッチ実行 (run_recommendation_jobs.sh)
  0) 終了
MENU
        read -r -p "番号を入力 > " choice
        case "$choice" in
            1)
                continue
                ;;
            2)
                run_dev_start
                ;;
            3)
                run_start_server
                ;;
            4)
                run_ai_generator
                ;;
            5)
                run_flow_generator
                ;;
            6)
                run_tests_interactive
                ;;
            7)
                pip install -r requirements.txt
                print_info "requirements.txt がインストールされました"
                ;;
            8)
                run_migrations
                ;;
            9)
                run_recommendation_job
                ;;
            0)
                print_info "終了します"
                break
                ;;
            *)
                print_warning "0〜8の番号を入力してください"
                ;;
        esac
    done
}

usage() {
    cat <<USAGE
使い方: $(basename "$0") [command]

command:
  menu        対話型メニューを開く (デフォルト)
  info        現在のプロジェクト状況を表示
  setup       dev_start.sh を実行
  start       start_server.sh を実行
  ai          ai_generate_spots.sh を実行
  flow [URL]  フロー図を生成 (URL省略時は http://127.0.0.1:8000/)
  test [ARGS] manage.py test を実行 (ARGS は任意指定)
  install_requirements requirements.txt をインストール
  migrate     makemigrations && migrate を実行
  recommend [ARGS] run_recommendation_jobs.sh を実行
  help        このメッセージを表示
USAGE
}

run_cli() {
    local command="$1"
    shift || true

    case "$command" in
        menu)
            show_menu
            ;;
        info)
            show_overview
            ;;
        setup)
            run_dev_start
            ;;
        start)
            run_start_server
            ;;
        ai)
            run_ai_generator
            ;;
        flow)
            local url="${1:-http://127.0.0.1:8000/}"
            if ! python_cmd=$(resolve_python); then
                print_error "Pythonが見つからないためフロージェネレーターを実行できません"
                exit 1
            fi
            print_header "画面フロー図を生成します"
            (cd "$ROOT_DIR" && "$python_cmd" "$SCRIPTS_DIR/flow/generate_flow.py" --base-url "$url")
            ;;
        test)
            run_tests "$@"
            ;;
        migrate)
            run_migrations
            ;;
        recommend)
            bash "$SCRIPTS_DIR/run_recommendation_jobs.sh" "$@"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            print_error "不明なコマンド: $command"
            usage
            exit 1
            ;;
    esac
}

main() {
    if [ $# -eq 0 ]; then
        show_menu
        return
    fi

    run_cli "$@"
}

main "$@"

