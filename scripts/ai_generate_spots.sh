#!/bin/bash

# AIスポット生成スクリプト
# LM Studioを使用してAIが観光スポットを自動生成し、サーバーを起動します

set -e

# 色付きの出力用関数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

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
    echo -e "\033[36m🤖 $1\033[0m"
}

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

print_header "AIスポット生成モード"
echo ""

# 仮想環境の確認と有効化
if [ ! -d "venv" ]; then
    print_error "仮想環境が見つかりません。先に開発セットアップを実行してください。"
    echo ""
    print_info "実行方法: ./start.sh を実行して選択肢2を選んでください"
    exit 1
fi

print_info "仮想環境を有効化しています..."
source venv/bin/activate

# Djangoの確認
if ! python -c "import django" 2>/dev/null; then
    print_error "Djangoがインストールされていません。先に開発セットアップを実行してください。"
    exit 1
fi

# LM Studioの接続確認
print_info "LM Studioの接続を確認しています..."
LMSTUDIO_BASE_URL=${LMSTUDIO_BASE_URL:-"http://localhost:1234/v1"}
LMSTUDIO_MODEL=${LMSTUDIO_MODEL:-"qwen/qwen3-4b-2507"}

if ! curl -s --connect-timeout 5 "$LMSTUDIO_BASE_URL/models" > /dev/null 2>&1; then
    print_warning "LM Studioに接続できません。"
    echo ""
    print_info "LM Studioの設定:"
    print_info "1. LM Studioを起動"
    print_info "2. Local Serverを開始"
    print_info "3. OpenAI互換APIを有効化"
    print_info "4. ポート1234でサーバーを起動"
    print_info "5. モデル '$LMSTUDIO_MODEL' をロード"
    echo ""
    print_info "環境変数の設定:"
    print_info "export LMSTUDIO_BASE_URL='http://localhost:1234/v1'"
    print_info "export LMSTUDIO_MODEL='qwen/qwen3-4b-2507'"
    echo ""
    read -p "LM Studioの準備ができましたか？ (y/N): " lmstudio_ready
    if [[ ! "$lmstudio_ready" =~ ^[Yy]$ ]]; then
        print_info "LM Studioの準備ができたら再度実行してください。"
        exit 0
    fi
fi

# 生成するスポット数の入力
echo ""
print_info "生成するスポット数を入力してください:"
echo "1) 5個のスポット"
echo "2) 10個のスポット"
echo "3) 20個のスポット"
echo "4) カスタム数"
echo ""

while true; do
    read -p "選択してください (1-4): " spot_choice
    case $spot_choice in
        1)
            spot_count=5
            break
            ;;
        2)
            spot_count=10
            break
            ;;
        3)
            spot_count=20
            break
            ;;
        4)
            while true; do
                read -p "生成するスポット数を入力してください (1-50): " custom_count
                if [[ "$custom_count" =~ ^[0-9]+$ ]] && [ "$custom_count" -ge 1 ] && [ "$custom_count" -le 50 ]; then
                    spot_count=$custom_count
                    break
                else
                    print_warning "1から50の間の数値を入力してください。"
                fi
            done
            break
            ;;
        *)
            print_warning "無効な選択です。1、2、3、または4を入力してください。"
            ;;
    esac
done

# データベースマイグレーション
print_info "データベースマイグレーションをチェックしています..."
if ! python manage.py migrate --check 2>/dev/null; then
    print_info "データベースマイグレーションを実行しています..."
    python manage.py migrate
fi

# AIスポット生成の実行
echo ""
print_info "AIスポット生成を開始します..."
print_info "生成数: $spot_count 個"
print_info "モデル: $LMSTUDIO_MODEL"
print_info "ベースURL: $LMSTUDIO_BASE_URL"
echo ""

python manage.py ai_generate_spots "$spot_count"

if [ $? -eq 0 ]; then
    print_success "AIスポット生成が完了しました！"
else
    print_error "AIスポット生成に失敗しました。"
    exit 1
fi

# Django開発サーバーを起動
echo ""
print_info "Django開発サーバーを起動しています..."
print_info "📍 サーバーURL: http://127.0.0.1:8000/"
print_info "📍 管理画面: http://127.0.0.1:8000/admin/"
print_info "⏹️  停止するには Ctrl+C を押してください"
echo ""

python manage.py runserver