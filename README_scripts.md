# Django開発サーバー起動スクリプト

このプロジェクトには、Django開発サーバーを簡単に起動するためのスクリプトが含まれています。

## 📁 スクリプト構造

```
TripLog/
├── start.sh              # メイン起動スクリプト（選択機能付き）
└── scripts/
    ├── start_server.sh   # 通常起動スクリプト
    ├── dev_start.sh      # フルセットアップスクリプト
    └── ai_generate_spots.sh # AIスポット生成スクリプト
```

## 🚀 使用方法

### メインスクリプト（推奨）
```bash
./start.sh
```

このスクリプトを実行すると、以下の選択肢が表示されます：

1. **🚀 通常起動** - 仮想環境が既に作成済みの場合
2. **🔧 開発セットアップ** - 初回セットアップや環境を一から構築したい場合
3. **🤖 AIスポット生成** - AIが観光スポットを自動生成（LM Studioが必要）
4. **❌ 終了**

### 直接実行（上級者向け）

#### 通常起動
```bash
./scripts/start_server.sh
```

**機能:**
- 仮想環境の有効化
- Djangoのインストール確認
- データベースマイグレーションの実行
- 開発サーバーの起動

#### フルセットアップ
```bash
./scripts/dev_start.sh
```

**機能:**
- Pythonバージョンの確認
- 仮想環境の作成（存在しない場合）
- pipのアップグレード
- requirements.txtからの依存関係インストール
- Djangoのインストール確認
- データベースマイグレーション
- 静的ファイルの収集
- 開発サーバーの起動

#### AIスポット生成
```bash
./scripts/ai_generate_spots.sh
```

**機能:**
- LM Studioの接続確認
- 生成スポット数の選択（5/10/20/カスタム）
- AIによる観光スポットの自動生成
- データベースマイグレーション
- 開発サーバーの起動

**前提条件:**
- LM Studioが起動している
- OpenAI互換APIが有効化されている
- モデル（デフォルト: qwen/qwen3-4b-2507）がロードされている

## 📍 アクセス先

- **メインサイト:** http://127.0.0.1:8000/
- **管理画面:** http://127.0.0.1:8000/admin/

## 🚀 クイックスタート

```bash
./start.sh
```

実行後、状況に応じて選択肢を選んでください：
- **初回の場合:** 2を選択（開発セットアップ）
- **2回目以降:** 1を選択（通常起動）
- **AIスポット生成:** 3を選択（LM Studioが必要）

## ⚠️ 注意事項

- スクリプトを実行する前に、プロジェクトのルートディレクトリにいることを確認してください
- 初回実行時は開発セットアップモード（選択肢2）を使用することを推奨します
- サーバーを停止するには `Ctrl+C` を押してください

## 🔧 トラブルシューティング

### 権限エラーが発生する場合
```bash
chmod +x start.sh
chmod +x scripts/start_server.sh
chmod +x scripts/dev_start.sh
chmod +x scripts/ai_generate_spots.sh
```

### 仮想環境が見つからない場合
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Djangoがインストールされていない場合
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### LM Studioの設定（AIスポット生成用）

AIスポット生成機能を使用するには、LM Studioの設定が必要です：

1. **LM Studioのインストール**
   - [LM Studio](https://lmstudio.ai/)をダウンロード・インストール

2. **モデルのダウンロード**
   - LM Studioで「qwen/qwen3-4b-2507」モデルをダウンロード
   - または他のモデルを使用する場合は環境変数を設定

3. **Local Serverの起動**
   - LM Studioで「Local Server」タブを開く
   - ポート1234でサーバーを起動
   - OpenAI互換APIを有効化

4. **環境変数の設定（オプション）**
   ```bash
   export LMSTUDIO_BASE_URL="http://localhost:1234/v1"
   export LMSTUDIO_MODEL="qwen/qwen3-4b-2507"
   ```

5. **AIスポット生成の実行**
   ```bash
   ./start.sh
   # 選択肢3を選択
   ```