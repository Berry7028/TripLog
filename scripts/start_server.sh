#!/bin/bash

# Django開発サーバー起動スクリプト
# 仮想環境を有効化してDjangoサーバーを起動します

echo "🚀 Django開発サーバーを起動しています..."

# プロジェクトのルートディレクトリに移動
cd "$(dirname "$0")/.."

# 仮想環境が存在するかチェック
if [ ! -d "venv" ]; then
    echo "❌ 仮想環境が見つかりません。venv/フォルダが存在することを確認してください。"
    exit 1
fi

# 仮想環境を有効化
echo "📦 仮想環境を有効化しています..."
source venv/bin/activate

# Djangoがインストールされているかチェック
if ! python -c "import django" 2>/dev/null; then
    echo "❌ Djangoがインストールされていません。requirements.txtから依存関係をインストールしてください。"
    echo "実行コマンド: pip install -r requirements.txt"
    exit 1
fi

# データベースマイグレーションを実行（必要に応じて）
echo "🗄️  データベースマイグレーションをチェックしています..."
python manage.py migrate --check 2>/dev/null || {
    echo "📝 データベースマイグレーションを実行しています..."
    python manage.py migrate
}

# Django開発サーバーを起動
echo "🌐 Django開発サーバーを起動しています..."
echo "📍 サーバーURL: http://127.0.0.1:8000/"
echo "⏹️  停止するには Ctrl+C を押してください"
echo ""

python manage.py runserver