# TripLog

Render.com にデプロイされた Django ベースの旅行ログマッピングアプリケーションです。インタラクティブな地図を通じて旅先スポットを共有・発見できます。

## 機能

- 旅行スポットを探索できるインタラクティブマップ
- ユーザー認証と旅行ログの共有機能
- **AIベースのパーソナライズドおすすめ機能** (新機能!)
  - ユーザーの閲覧履歴を分析して最適なスポットを提案
  - バックグラウンドで1時間ごとにスコアを更新
  - 未閲覧のスポットも関連性に基づいて推薦
- 本番デプロイ時の自動スーパーユーザー作成
- デプロイ後セットアップの自動化

## デプロイ設定

### 環境変数

Render.com で本番デプロイする際は、以下の環境変数を設定してください。

#### Django 用必須設定
- `SECRET_KEY`: セキュリティのための Django シークレットキー
- `DEBUG`: 本番環境では `false` に設定
- `DATABASE_URL`: Render が自動で提供する PostgreSQL の接続 URL

#### スーパーユーザー自動作成
デプロイ時に管理者アカウントを自動作成する場合は、以下の環境変数をセットします。

- `DJANGO_SUPERUSER_USERNAME`: 管理者ユーザー名（例: `admin`）
- `DJANGO_SUPERUSER_EMAIL`: 管理者メールアドレス
- `DJANGO_SUPERUSER_PASSWORD`: 管理者パスワード（例: `admin123`）

### 自動デプロイ手順

1. **データベース初期化**: `python manage.py migrate`
2. **静的ファイル収集**: `python manage.py collectstatic --no-input`
3. **デプロイ後処理**: `post_deploy.sh` を実行してスーパーユーザーを作成
4. **サーバー起動**: Gunicorn サーバーを起動

### ファイル構成

```
├── post_deploy.sh          # スーパーユーザー作成用のデプロイ後スクリプト
├── start.sh                # デプロイ時のメイン起動スクリプト
├── requirements.txt        # Python 依存パッケージ
├── manage.py               # Django 管理コマンド
├── travel_log_map/         # Django プロジェクト設定
└── spots/                  # 旅行スポット用 Django アプリ
```

### 手動デプロイ手順

1. リポジトリをクローン
2. 依存関係をインストール: `pip install -r requirements.txt`
3. 環境変数を設定
4. マイグレーション実行: `python manage.py migrate`
5. スーパーユーザー作成: `python manage.py createsuperuser`
6. 開発サーバー起動: `python manage.py runserver`

## 管理画面アクセス

デプロイ後、管理画面には以下からアクセスします。
- **URL**: `https://your-domain.com/admin/`
- **ユーザー名**: `DJANGO_SUPERUSER_USERNAME` で指定した値
- **パスワード**: `DJANGO_SUPERUSER_PASSWORD` で指定した値

## 開発

### ローカルセットアップ

```bash
git clone https://github.com/Berry7028/TripLog.git
cd TripLog
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### スクリプト

- `start.sh`: 本番環境向けの起動スクリプト(デプロイ後セットアップ込み)
- `post_deploy.sh`: 環境変数を用いたスーパーユーザー自動作成スクリプト
- `scripts/run_recommendation_jobs.sh`: AIおすすめ解析バッチジョブ
- 開発用スクリプトは `scripts/` ディレクトリを参照

## AIおすすめ機能

### 概要

ユーザーの閲覧履歴を分析し、パーソナライズされたスポット推薦を提供します。

### 仕組み

1. **バックグラウンド解析**: 1時間ごとに全ユーザーの閲覧データを分析
2. **AIスコアリング**: OpenRouter API を使用して各スポットにスコアを付与
3. **DB保存**: 計算結果をデータベースに保存し、即座に表示可能
4. **未閲覧スポット推薦**: ユーザーが見ていないスポットも関連性に基づいて推薦

### 設定

環境変数に以下を設定してください:

```bash
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_RECOMMENDATION_MODEL=openai/gpt-4o-mini  # 任意
OPENROUTER_TIMEOUT=15  # 任意
```

### バックグラウンドジョブの実行

```bash
# 全ユーザーのスコアを計算(スケジュールに従う)
python manage.py run_recommendation_jobs

# 強制実行(スケジュール無視)
python manage.py run_recommendation_jobs --force

# 特定ユーザーのみ
python manage.py run_recommendation_jobs --username=admin

# シェルスクリプト経由
bash scripts/run_recommendation_jobs.sh --force
```

### Cron設定例(1時間ごと)

```bash
0 * * * * cd /path/to/TripLog && python manage.py run_recommendation_jobs
```

### 管理画面での確認

- **おすすめ解析設定**: `/admin/spots/recommendationjobsetting/`
- **解析ログ**: `/admin/spots/recommendationjoblog/`
- **ユーザースコア**: `/admin/spots/userrecommendationscore/`

## 技術スタック

- **バックエンド**: Django 5.2+
- **データベース**: PostgreSQL（本番）、SQLite（開発）
- **デプロイ**: Render.com
- **アプリケーションサーバー**: Gunicorn
- **静的ファイル**: WhiteNoise

## コントリビューション

開発ガイドラインと利用可能なスクリプトについては `AGENTS.md` と `README_scripts.md` を参照してください。

## ライセンス

本プロジェクトは非公開であり、一般公開用のライセンスは付与していません。
