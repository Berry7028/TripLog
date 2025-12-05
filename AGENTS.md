# リポジトリガイドライン

## プロジェクト構成とモジュールの整理
`travel_log_map/` には Django の設定、URL、WSGI エントリポイントが含まれます。環境固有の調整は設定モジュール内に限定してください。機能ロジックはアプリディレクトリ（マップ表示用の `spots/`、認証用の `accounts/`、デプロイ補助の `manage_admin/`）に配置し、各アプリの `templates/` と `static/` フォルダに共通テンプレートや静的アセットを格納します。ルートレベルのスクリプト（`start.sh`、`post_deploy.sh`、`manage.py`）は運用を統括し、SQLite の開発データ（`db.sqlite3`）は PostgreSQL のフィクスチャが整ったらコミットしないでください。

## ビルド・テスト・開発コマンド
仮想環境を有効化した後（`python -m venv .venv && source .venv/bin/activate`）、`pip install -r requirements.txt` で依存関係をインストールします。スキーママイグレーションは `python manage.py migrate`、テストデータ作成は `python manage.py loaddata fixtures/<name>.json`、開発サーバー起動は `python manage.py runserver` です。本番環境に近づけるには `python manage.py collectstatic --no-input` を実行後、`./start.sh` でマイグレーション・管理者シード・Gunicorn 起動を連鎖します。`post_deploy.sh` スクリプトは `DJANGO_SUPERUSER_*` 変数が必要です。

## コーディングスタイルと命名規則
PEP 8 に従い、インデントは4スペース、Python関数はスネークケース、モデルやフォームクラスはキャメルケース、CSSクラスはケバブケースを使用します。Djangoアプリは薄く保ち、ビューのロジックが約40行を超える場合は `spots/services/` や `accounts/tasks/` に委譲してください。テンプレートは `templates/<app>/` に配置し、共通ベースレイアウトを継承します。プッシュ前に `python -m compileall` または任意のリンターをローカルで実行してください。`black` 導入までは一貫したシングルクォートと明示的な相対インポートを推奨します。

## テストガイドライン
ユニット・統合テストはアプリ構成を反映（例：`spots/tests/test_views.py`）し、pytestスタイルのメソッド名を使ってください（Djangoのランナー `python manage.py test spots` でも実行可能）。シリアライザー、権限ゲート、レンダリングヘルパーを網羅し、新しいエンドポイントにはハッピーパスと失敗テストを最低1つずつ追加します。遅いジオコーディングテストには `@skipUnless` ガードを付け、CIの高速化を図ります。

## コミット・プルリクエストガイドライン
基本ブランチは `main` と `develop` です。機能追加は `develop` から（`feature/<ticket>-short-description`）、ホットフィックスは `main` から分岐します。コミット件名は命令形（例：`Add map tile caching`）で、関連変更を論理的にまとめてください。PRは元の課題へのリンク、マイグレーションや環境変数の影響説明、UI調整の場合はスクリーンショット、手動テスト手順（例：`python manage.py runserver` でサンプルデータ確認）を含めます。

## コミットメッセージの例

コミットメッセージは必ず `feat: `（新機能追加）、`fix: `（バグ修正）、`docs: `（ドキュメント変更）、`refactor: `（リファクタリング）、`test: `（テスト追加・修正）などのプリフィックスを先頭につけてください。

例:
```
feat: Add user authentication with email verification
- Implemented custom user model in accounts app
- Added email verification workflow using Django signals
- Updated registration and login templates
- Added unit tests for user model and authentication views
```

## セキュリティと設定のヒント
秘密情報は `.env` やホスティングプロバイダーのダッシュボードに保存し、Gitには絶対に含めないでください。必要なキーは `SECRET_KEY`、`DEBUG`、`DATABASE_URL`（または管理Postgres用の個別 `DB_*` 変数）、自動化利用時の `DJANGO_SUPERUSER_*` です。Webhookやマッププロバイダーのテスト時は一時APIキーを毎回ローテーションし、機密ログはコミット前に消去してください。

## レスポンスルール
常に日本語で回答をする、既存のコードスタイルに従う、必要最低限のコメントのみし、必要でないコードは書かない
新しく外部のライブラリを導入する時必ずrequirements.txtに追記をする
