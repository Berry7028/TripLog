# TripLog エージェントガイド

## プロジェクト概要
TripLogは、AIによるパーソナライズドなレコメンドを備えたDjango製の旅行スポット共有プラットフォームです。ユーザーはインタラクティブな地図を通じて旅行先を発見・共有・探索できます。

**主要技術スタック**: Django 5.2 / PostgreSQL・SQLite / OpenRouter API / Render.com デプロイ

## アーキテクチャとデータフロー

### 主要コンポーネント
- **`travel_log_map/`**: Djangoの設定、URLルーティング、WSGI/ASGIエントリポイント
- **`spots/`**: ビジネスロジック（モデル、ビュー、テンプレート、サービス）を含むメインアプリ
- **`scripts/`**: 開発用ユーティリティと自動化スクリプト
- **`spots/services/`**: 分析やレコメンドジョブといったビジネスロジック層

### リクエストフロー
```
URLs (travel_log_map/urls.py → spots/urls.py)
    ↓
Views (spots/views.py)
    ↓
Services (spots/services/analytics.py, recommendation_jobs.py)
    ↓
Models (spots/models.py)
    ↓
Database (PostgreSQL/SQLite)
```

## AIレコメンドシステム
**データ収集**: `UserSpotInteraction`モデルで閲覧回数・滞在時間・タイムスタンプを記録。

**スコアリングプロセス**:
1. バックグラウンドジョブ（`run_recommendation_jobs`）が1時間ごとにユーザー履歴を解析。
2. OpenRouter APIへユーザー行動データを送信。
3. AIが各スポットの関連度スコア（0〜100）を生成。
4. 結果を`UserRecommendationScore`に保存し、高速に参照。
5. トップページでパーソナライズした並び順を提供。

**フォールバックロジック**: APIが利用できない場合は、閲覧回数・新規性・滞在時間のヒューリスティックでソート。

## プロジェクト構成とモジュール整理
- `travel_log_map/`は設定・ルーティング・エントリポイントを保持。
- 機能コードは`spots/`（モデル・ビュー・テンプレート・静的ファイル・マイグレーション）。
- テンプレートは`spots/templates/spots/`、静的ファイルは`spots/static/spots/`に配置。
- テストは対象モジュールに対応させて`spots/tests/`へ配置。
- スクリプトや開発補助は`scripts/`へ。
- `db.sqlite3`と`media/`はコミット対象外（開発アーティファクト）。
- 依存関係は`venv/`で分離管理。

## 開発ワークフロー

### 環境構築
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 主なコマンド
- `python manage.py runserver`
- `python manage.py makemigrations && python manage.py migrate`
- `python manage.py run_recommendation_jobs --force`
- `python manage.py ai_generate_spots <count>`
- `python manage.py test spots`

### 開発ハブ
`./start.sh` または `./scripts/devhub/devhub.sh menu`でインタラクティブなワークフロー用ダッシュボードを起動。

## コーディングスタイルとパターン

### コーディング規約
- PEP 8に従い、インデントは4スペース・エンコードはUTF-8。
- モジュール・関数・変数は`snake_case`、クラスは`CapWords`。
- テンプレート名は`lowercase_with_underscores.html`。
- ビューは`spots/views.py`もしくは機能別モジュールに配置。
- ルート登録は`spots/urls.py`で安定した名前（例: `add_spot`, `spot_detail`）。
- アセットは`{% static 'spots/<path>' %}`で読み込む。

### モデル間の関係
```python
# カスケード関係を持つ主要エンティティ
class Spot(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)

class UserSpotInteraction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    # ユーザー×スポットでレコードを一意に維持

class UserRecommendationScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(Spot, on_delete=models.CASCADE)
    # 事前計算したAIスコアで高速ソート
```

### サービスレイヤーパターン
ビジネスロジックは`spots/services/`に分離。
- `analytics.py`: AIスコアとスポット関連度計算。
- `recommendation_jobs.py`: バックグラウンドジョブのオーケストレーションとツールコール。

### AI連携パターン
```python
# LLM向けのツールスキーマを定義

def build_recommendation_tool_schema():
    return [{
        'type': 'function',
        'function': {
            'name': 'store_user_recommendation_scores',
            'parameters': {
                'type': 'object',
                'properties': {
                    'user_id': {'type': 'integer'},
                    'scores': {'type': 'array', 'items': {'type': 'object'}}
                }
            }
        }
    }]

# LLMレスポンスからのツールコールを処理

def store_recommendation_scores(arguments: Dict[str, Any]):
    # LLMの返却値を解析してDBへ保存
    scores = arguments.get('scores', [])
    UserRecommendationScore.objects.bulk_create([...])
```

### バックグラウンドジョブのスケジューリング
```python
# 実行間隔を基にジョブ実行可否を判定

def is_job_due(setting: RecommendationJobSetting):
    elapsed = timezone.now() - setting.last_run_at
    return elapsed.total_seconds() >= setting.interval_hours * 3600

# ユーザー履歴を持つ全ユーザーに対して処理

def compute_and_store_all_user_scores():
    users_with_history = User.objects.filter(
        spot_interactions__isnull=False
    ).distinct()
```

### ビューとURLのパターン
```python
# spots/urls.py - 機能別に整理したルーティング
urlpatterns = [
    path('', views.home, name='home'),
    path('spot/<int:spot_id>/', views.spot_detail, name='spot_detail'),
    path('api/spots/', views.spots_api, name='spots_api'),
    path('api/search/', views.search_spots_api, name='search_spots_api'),
    path('manage/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('manage/spots/', admin_views.SpotAdminListView.as_view(), name='admin_spot_list'),
]

# spot_detail内での閲覧トラッキング

def spot_detail(request, spot_id):
    spot = get_object_or_404(Spot, id=spot_id)
    if request.method == 'GET':
        SpotView.objects.create(spot=spot)
        if request.user.is_authenticated:
            interaction, _ = UserSpotInteraction.objects.get_or_create(
                user=request.user, spot=spot,
                defaults={'view_count': 1}
            )
            interaction.view_count = F('view_count') + 1
            interaction.save()
```

## テスト指針
- テストは`spots/tests/`でアプリ構成に合わせて整理。
- クラス名は`Test<Model><Action>`（例: `TestSpotDetailView`）。
- メソッド名は`test_<action>_<condition>`（例: `test_get_authenticated_user`）。
- 大規模フィクスチャよりもインライン生成やヘルパーを活用。
- ステータスコード、コンテキストデータ、副作用を検証。
- レビュー前に`python manage.py test`または`python manage.py test spots`をクリーンに。

```python
def test_spot_detail_view(self):
    spot = Spot.objects.create(title="Test Spot", ...)
    response = self.client.get(f'/spot/{spot.id}/')
    self.assertEqual(response.status_code, 200)
    self.assertTrue(SpotView.objects.filter(spot=spot).exists())
```

## よくある開発タスク

### 新機能追加
1. `spots/models.py`でモデル変更を定義。
2. `python manage.py makemigrations`でマイグレーションを生成。
3. `spots/views.py`にビュー処理を実装。
4. `spots/urls.py`へルートを追加。
5. `spots/templates/spots/`のテンプレートを作成・更新。
6. 必要に応じて`spots/admin_views.py`の管理画面を拡張。

### AI機能開発
1. サービス層でツールスキーマを定義。
2. API連携ロジックを実装。
3. テスト用の管理コマンドを追加。
4. バックグラウンドジョブをスケジュール。
5. 監視用に管理画面を更新。

### AIレコメンドのデバッグ
1. ユーザー行動: `UserSpotInteraction.objects.filter(user=user)`。
2. レコメンドスコア: `UserRecommendationScore.objects.filter(user=user)`。
3. ジョブログ: `RecommendationJobLog.objects.filter(user=user)`。
4. 手動スコアリング: `python manage.py run_recommendation_jobs --username=testuser --dry-run`。

## デプロイと設定

### 環境変数
```bash
# Djangoコア
SECRET_KEY=your-secret-key
DEBUG=false
DATABASE_URL=postgresql://...

# AIサービス
OPENROUTER_API_KEY=your-openrouter-key
OPENROUTER_RECOMMENDATION_MODEL=openai/gpt-4o-mini

# LM Studio (開発)
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LMSTUDIO_MODEL=qwen/qwen3-4b-2507
```

### 本番デプロイ
- Render.comでGunicorn運用。
- 本番はPostgreSQL、ローカルはSQLite。
- 静的ファイルはWhiteNoiseミドルウェアで提供。
- `post_deploy.sh`でスーパーユーザー作成を自動化。

### セキュリティと設定の注意点
- 秘密情報は環境変数や無視対象の`.env`から取得し、ハードコードしない。
- `DEBUG=True`と広い`ALLOWED_HOSTS`はローカルのみに限定。
- 本番では`DEBUG=False`、`ALLOWED_HOSTS`と`CSRF_TRUSTED_ORIGINS`を見直す。
- ストレージ、地図API、外部連携を追加する際は`travel_log_map/settings.py`を更新。

## コミットとプルリクエストの指針
- コミットは小さく命令形で焦点を絞る（例: `Add spot detail view`）。
- 必要に応じて`Fixes #id`で課題を関連付け。
- PRでは変更内容、手動テスト手順、UI更新時はスクリーンショットを記載。
- マイグレーションや設定変更は明示的に共有。
- レビュアー負荷を下げるため、PRは概ね300行以内に。

## ファイル構成の原則

### テンプレート
```
spots/templates/spots/
├── base.html
├── home.html
├── spot_detail.html
├── add_spot.html
└── registration/
    └── register.html
```

### 静的アセット
```
spots/static/spots/
├── css/
├── js/
└── images/
```

### 管理コマンド
```
spots/management/commands/
├── run_recommendation_jobs.py
└── ai_generate_spots.py
```

備考: TripLogはAIによるパーソナライズ、バックグラウンドジョブの堅牢性、ビュー層とサービス層の明確な分離を重視します。新機能を追加する際は、レコメンドシステムやユーザー行動トラッキングとの整合性を常に意識してください。
