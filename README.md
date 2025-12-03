# TripLog

Django で作られた旅行ログマッピングアプリです。Render などのクラウドへデプロイして、旅先スポットを地図上で共有・閲覧できます。

## 主な機能
- 旅行スポットを地図上で探索・閲覧
- ユーザー認証と旅行ログの共有
- スーパーユーザー自動作成を含むデプロイ後セットアップスクリプト
- WhiteNoise を使った本番環境での静的ファイル配信

## 前提条件
- Python 3.11 以上（推奨：3.12）
- pip（`python -m ensurepip --upgrade` で準備可能）
- PostgreSQL（本番環境）。開発では SQLite を自動使用

## 早わかりセットアップ
```bash
# 1. リポジトリを取得
git clone https://github.com/Berry7028/TripLog.git
cd TripLog

# 2. 仮想環境を作成・有効化（任意）
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate

# 3. 依存関係をインストール
pip install -r requirements.txt

# 4. 環境変数を用意（.env など）
#    SECRET_KEY、DEBUG、DATABASE_URL などを設定

# 5. マイグレーション & 管理ユーザー作成
python manage.py migrate
python manage.py createsuperuser

# 6. 開発サーバーを起動
python manage.py runserver
```

## 環境変数
開発では `.env` もしくは `.env.local` に以下を設定してください。

| 変数 | 役割 | 備考 |
| ---- | ---- | ---- |
| `SECRET_KEY` | Django シークレットキー | 未設定時は開発向け値を使用します。必ず本番では独自値を設定してください。 |
| `DEBUG` | デバッグモード | `True` で開発モード、`False` で本番設定。未設定時は `True`。 |
| `DATABASE_URL` | DB 接続文字列 | Render などのホストで自動付与される URL に対応。未設定時は SQLite を使用。 |
| `DB_ENGINE` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL などの手動接続設定 | `DATABASE_URL` を使わない本番環境向け。`DEBUG=False` 時のみ参照されます。 |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` | デプロイ後に自動作成する管理者情報 | `post_deploy.sh` で利用されます。 |

## 開発時の使い方
1. **依存関係のインストール**: `pip install -r requirements.txt`
2. **マイグレーション**: `python manage.py migrate`
3. **管理ユーザー作成（任意）**: `python manage.py createsuperuser`
4. **サーバー起動**: `python manage.py runserver`

### 静的ファイル
- 開発: `spots/static/` を自動参照します。
- 本番: `python manage.py collectstatic --no-input` で `staticfiles/` に収集され、WhiteNoise で配信されます。

## デプロイ
Render を想定した本番起動例です。

1. 環境変数を設定（`SECRET_KEY`, `DEBUG=False`, `DATABASE_URL` など）。
2. スタートコマンドに `./start.sh` を設定。
   - スクリプト内で静的ファイル収集、マイグレーション、`post_deploy.sh` によるスーパーユーザー自動作成を行い、最後に Gunicorn を起動します。

### 手動デプロイ手順
```bash
python manage.py collectstatic --no-input
python manage.py migrate
./post_deploy.sh  # スーパーユーザー自動作成（環境変数必須）
gunicorn travel_log_map.wsgi:application --bind 0.0.0.0:$PORT
```

## Debug Tools
Django html で Emmetのサポートをしています
またhtmlを編集しセーブをしたらブラウザーのホットリロードが入るようなシステムを導入しています

## プロジェクト構成
```
├── manage.py               # Django 管理コマンドエントリ
├── post_deploy.sh          # デプロイ後のスーパーユーザー自動作成スクリプト
├── start.sh                # 本番向け起動スクリプト（Render 用）
├── requirements.txt        # 依存パッケージ
├── travel_log_map/         # プロジェクト設定
└── spots/                  # 旅行スポット用アプリ
```

## テスト
現在、自動テストは未整備です。必要に応じて `python manage.py test` を利用してください。

## ライセンス
本プロジェクトは非公開であり、一般公開用のライセンスは付与していません。
