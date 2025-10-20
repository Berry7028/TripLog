# TripLog Next.js フロントエンド

Django 製 TripLog のテンプレート UI を Next.js + Tailwind CSS に移行したフロントエンドです。Django 側の JSON API (`/api/...`) を利用してページを構築します。

## セットアップ

```bash
cd frontend
npm install
npm run dev
```

デフォルトでは `http://localhost:8000` の Django サーバーに接続します。デプロイ時は `.env.local` などの環境ファイルに API のベース URL を設定してください。

```bash
# 最低限この変数を指定すればフロントエンドとバックエンドを別ホストに配置できます
NEXT_PUBLIC_DJANGO_BASE_URL=https://api.example.com

# ほかにも以下の環境変数名を認識します（必要なものだけ設定してください）
# NEXT_PUBLIC_API_BASE_URL=https://api.example.com
# NEXT_PUBLIC_BACKEND_URL=https://api.example.com
# API_BASE_URL=https://api.example.com
# DJANGO_API_BASE_URL=https://api.example.com
# BACKEND_URL=https://api.example.com
```

`frontend/.env.example` にサンプル値も用意しています。必要な値をコピーして `.env.local`（開発）や本番の環境変数に適用してください。

## 主なページ

- `/` ホーム（検索・おすすめ順）
- `/spots/[id]` スポット詳細、レビュー、お気に入り
- `/spots/add` スポット投稿（ログイン必須）
- `/ranking` ランキング
- `/map` 最新スポットの地図表示
- `/plan` 外部プランナーの埋め込み
- `/my-spots` 自分の投稿一覧
- `/profile` プロフィール編集
- `/login`, `/register` 認証

## API 連携

Next.js の API Routes 経由で Django のセッション Cookie を共有しています。ログインや投稿などの操作は `/api/...` にプロキシされます。
