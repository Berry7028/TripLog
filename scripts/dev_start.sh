#!/bin/bash

# Django開発環境セットアップ・起動スクリプト
# 仮想環境の作成、依存関係のインストール、サーバー起動を自動化します

set -e  # エラーが発生したらスクリプトを停止

echo "🚀 Django開発環境をセットアップしています..."

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

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

# Pythonのバージョンチェック
print_info "Pythonのバージョンをチェックしています..."
python3 --version

# 仮想環境の作成または確認
if [ ! -d "venv" ]; then
    print_info "仮想環境を作成しています..."
    python3 -m venv venv
    print_success "仮想環境が作成されました"
else
    print_success "仮想環境が見つかりました"
fi

# 仮想環境を有効化
print_info "仮想環境を有効化しています..."
source venv/bin/activate

# pipのアップグレード
print_info "pipをアップグレードしています..."
pip install --upgrade pip

# 依存関係のインストール
if [ -f "requirements.txt" ]; then
    print_info "依存関係をインストールしています..."
    pip install -r requirements.txt
    print_success "依存関係のインストールが完了しました"
else
    print_warning "requirements.txtが見つかりません"
fi

# Djangoのインストール確認
if ! python -c "import django" 2>/dev/null; then
    print_error "Djangoがインストールされていません"
    exit 1
fi

print_success "Djangoが正常にインストールされています"

# データベースマイグレーション
print_info "データベースマイグレーションをチェックしています..."
if ! python manage.py migrate --check 2>/dev/null; then
    print_info "データベースマイグレーションを実行しています..."
    python manage.py migrate
    print_success "マイグレーションが完了しました"
else
    print_success "データベースは最新の状態です"
fi

# 静的ファイルの収集（本番環境用）
print_info "静的ファイルを収集しています..."
python manage.py collectstatic --noinput

# Django開発サーバーを起動
echo ""
print_success "🎉 セットアップが完了しました！"
echo ""
print_info "🌐 Django開発サーバーを起動しています..."
print_info "📍 サーバーURL: http://127.0.0.1:8000/"
print_info "⏹️  停止するには Ctrl+C を押してください"
print_info "📝 管理画面: http://127.0.0.1:8000/admin/"
echo ""

python manage.py runserver