# TripLog

Django で作られた旅行ログマッピングアプリです。Railway を使って本番・テスト環境をホスティングし、旅先スポットを地図上で共有・閲覧できます。

## 主な機能
- 旅行スポットを地図上で探索・閲覧
- ユーザー認証と旅行ログの共有
- Railway 上の本番・プレビュー運用を想定した構成
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

## git & github に関すること
- 永続ブランチはmain, developブランチです。
- 機能追加や修正はdevelopブランチから新規ブランチを切って行い、完了後にdevelopへプルリクエストを送る
- デプロイとテスト（プレビュー）環境は Railway 上で運用します。通常は main を Production Deploy、PR/feature ブランチを Preview Deploy として扱います。
- GitHub Actions（`.github/workflows/django.yml`）で main / PR に対してマイグレーションとテストを実行します。
- 簡単なことだったら直接developブランチへpushしてもいい


## 環境変数
開発では `.env` もしくは `.env.local` に以下を設定してください。

| 変数 | 役割 | 備考 |
| ---- | ---- | ---- |
| `SECRET_KEY` | Django シークレットキー | 未設定時は開発向け値を使用します。必ず本番では独自値を設定してください。 |
| `DEBUG` | デバッグモード | `True` で開発モード、`False` で本番設定。未設定時は `True`。 |
| `DATABASE_URL` | DB 接続文字列 | Railway の Postgres を利用する場合に自動付与されます。未設定時は SQLite を使用。 |
| `DB_ENGINE` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` / `DB_HOST` / `DB_PORT` | PostgreSQL などの手動接続設定 | `DATABASE_URL` を使わない本番環境向け。`DEBUG=False` 時のみ参照されます。 |
| `DJANGO_SUPERUSER_USERNAME` / `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` | 管理ユーザー作成用の情報 | `createsuperuser --noinput` をスクリプト化する場合に利用できます（自動作成スクリプトは同梱していません）。 |
| `PORT` | バインドポート | Railway で自動設定されます。ローカルでは省略可。 |

## 開発時の使い方
1. **依存関係のインストール**: `pip install -r requirements.txt`
2. **マイグレーション**: `python manage.py migrate`
3. **管理ユーザー作成（任意）**: `python manage.py createsuperuser`
4. **サーバー起動**: `python manage.py runserver`

### 静的ファイル
- 開発: `spots/static/` を自動参照します。
- 本番: `python manage.py collectstatic --no-input` で `staticfiles/` に収集され、WhiteNoise で配信されます。

## デプロイ（Railway）
Railway を使って Production / Preview を運用する想定です。基本設定の例を示します。

1. Railway でプロジェクトを作成し、このリポジトリを GitHub 連携します。Production Deploy は main に紐付け、必要に応じて Preview Deploy（PR/feature ブランチ）を有効化してください。
2. 環境変数を設定します（`SECRET_KEY`, `DEBUG=False`, `DATABASE_URL` など）。Railway の Postgres を使う場合は `DATABASE_URL` が自動付与されます。
3. Start Command 例:
   ```bash
   python manage.py collectstatic --no-input && python manage.py migrate && gunicorn travel_log_map.wsgi:application --bind 0.0.0.0:$PORT
   ```
4. 初回のみ Railway のシェルで `python manage.py createsuperuser` を実行し、管理ユーザーを作成してください。

### 手動デプロイ手順（Railway と同等の構成）
```bash
python manage.py collectstatic --no-input
python manage.py migrate
gunicorn travel_log_map.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

## Debug Tools
Django html で Emmetのサポートをしています
またhtmlを編集しセーブをしたらブラウザーのホットリロードが入るようなシステムを導入しています

## プロジェクト構成
```
├── manage.py               # Django 管理コマンドエントリ
├── requirements.txt        # 依存パッケージ
├── .github/workflows/      # Django CI（テスト・マイグレーション）
├── .env.example            # 環境変数サンプル
├── travel_log_map/         # プロジェクト設定
└── spots/                  # 旅行スポット用アプリ
```

## テスト
ローカルでは `python manage.py test` を実行してください。GitHub Actions（`.github/workflows/django.yml`）で main / PR 向けにマイグレーションとテストが自動実行されます。

## ライセンス
本プロジェクトは非公開であり、一般公開用のライセンスは付与していません。
