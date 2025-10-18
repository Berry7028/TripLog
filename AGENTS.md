# Repository Guidelines

## プロジェクト構成とモジュール整理
- `travel_log_map/` はDjango設定、URL、WSGI/ASGIエントリポイントを保持し、全体のブートストラップを担います。
- `spots/` にモデル、ビュー、サービス、テンプレート、静的ファイルが集約されます。サービス層は `spots/services/` でAI分析やレコメンド処理を分離します。
- テンプレートは `spots/templates/spots/`、静的アセットは `spots/static/spots/` に配置し、追加素材は機能別サブディレクトリで整理してください。
- 自動化や補助スクリプトは `scripts/` にまとめ、テストコードは対象機能に合わせて `spots/tests/` 以下へ配置します。

## ビルド・テスト・開発コマンド
- `python -m venv venv && source venv/bin/activate` で仮想環境を準備し、`pip install -r requirements.txt` で依存関係を導入します。
- `python manage.py runserver` はローカル開発サーバーを起動し、`./start.sh` または `./scripts/devhub/devhub.sh menu` で対話型の開発ハブを開けます。
- モデル変更後は `python manage.py makemigrations && python manage.py migrate` を実行し、スキーマ整合性を保ちます。
- `python manage.py test spots` でアプリケーションテストを走らせ、`python manage.py run_recommendation_jobs --force` でAIレコメンドの強制再計算を行います。

## コーディングスタイルと命名規約
- PEP 8に従い、インデントは4スペース・UTF-8エンコードを維持します。型ヒントはサービス層や管理コマンドで積極的に追加してください。
- モジュール・関数・変数は `snake_case`、クラスは `CapWords`、テンプレートは `lowercase_with_underscores.html` を守ります。
- URL名は `spots/urls.py` で安定した識別子（例: `home`, `spot_detail`）を使用し、ビューとサービスの責務を分離してテスト容易性を高めます。
- 静的ファイル参照は `{% static 'spots/<path>' %}` を利用し、ビルド不要の軽量アセット構成を保ってください。

## テスト指針
- Django標準のテストフレームワークを使用し、クラスは `Test<Model><Action>`、メソッドは `test_<action>_<condition>` で命名します。
- ビューはステータスコードと副作用（例: `SpotView` 生成）を、サービスはAIスコアのフォールバック分岐を検証してください。
- 新規機能やバグ修正では `spots/tests/` に対応するモジュールテストを追加し、`python manage.py test spots` でローカル検証後にプッシュします。
- 主要フローのテストが存在しない場合はTODOを残さず、最低限のデータフィクスチャをインラインで組み立ててください。

## コミットとプルリクエストガイドライン
- コミットは小さな論理単位に分割し、命令形（例: `Add spot detail view`）で書きます。マイグレーションや設定変更はメッセージ内で明示しましょう。
- 既知のIssueと関連する場合は `Fixes #<id>` を追記し、追跡性を確保します。
- PRでは目的、変更点、手動テスト手順、UI変更時のスクリーンショット、マイグレーション有無を記載してください。
- CI通過を前提にレビューを依頼し、レビュー指摘は追加コミットで解消してからSquashするか、履歴を残したい場合のみRebaseしてください。

## セキュリティと設定のヒント
- 秘密情報は `.env` や環境変数から読み込み、リポジトリにハードコードしないでください。`SECRET_KEY` や `OPENAI_API_KEY` を共有環境で扱う際は権限管理を徹底します。
- 本番は `DEBUG=False` とし、`ALLOWED_HOSTS`・`CSRF_TRUSTED_ORIGINS` をデプロイ対象ドメインに限定します。
- バックエンドとAI推論の障害切り分けのため、`RecommendationJobLog` と管理コマンドのログを定期的に確認し、失敗時はフォールバックロジックの挙動をテストで再現してください。
