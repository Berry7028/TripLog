#!/bin/bash

# Django開発サーバー起動スクリプト
# 開発モードと通常モードを選択できます

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
    echo -e "\033[36m🚀 $1\033[0m"
}

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")"

print_header "Django開発サーバー起動スクリプト"
echo ""

# スクリプトディレクトリの存在確認
if [ ! -d "scripts" ]; then
    print_error "scripts/ディレクトリが見つかりません"
    exit 1
fi

# メニュー表示
echo "起動モードを選択してください:"
echo ""
echo "1) 🚀 通常起動 (仮想環境有効化 + サーバー起動)"
echo "   - 仮想環境が既に作成済みの場合"
echo "   - 依存関係がインストール済みの場合"
echo ""
echo "2) 🔧 開発セットアップ (フルセットアップ + サーバー起動)"
echo "   - 初回セットアップ時"
echo "   - 環境を一から構築したい場合"
echo ""
echo "3) 🤖 AIスポット生成 (スポット自動生成 + サーバー起動)"
echo "   - AIが観光スポットを自動生成"
echo "   - LM Studioが必要"
echo ""
echo "4) ❌ 終了"
echo ""

# ユーザー入力
while true; do
    read -p "選択してください (1-4): " choice
    case $choice in
        1)
            print_info "通常起動モードを選択しました"
            echo ""
            if [ -f "scripts/start_server.sh" ]; then
                bash scripts/start_server.sh
            else
                print_error "scripts/start_server.sh が見つかりません"
                exit 1
            fi
            break
            ;;
        2)
            print_info "開発セットアップモードを選択しました"
            echo ""
            if [ -f "scripts/dev_start.sh" ]; then
                bash scripts/dev_start.sh
            else
                print_error "scripts/dev_start.sh が見つかりません"
                exit 1
            fi
            break
            ;;
        3)
            print_info "AIスポット生成モードを選択しました"
            echo ""
            bash scripts/ai_generate_spots.sh
            break
            ;;
        4)
            print_info "終了します"
            exit 0
            ;;
        *)
            print_warning "無効な選択です。1、2、3、または4を入力してください。"
            ;;
    esac
done