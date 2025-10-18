# TripLog Next.js フロントエンド

Django 製 TripLog のテンプレート UI を Next.js + Tailwind CSS に移行したフロントエンドです。Django 側の JSON API (`/spots/api/...`) を利用してページを構築します。

## セットアップ

```bash
cd frontend
npm install
npm run dev
```

デフォルトでは `http://localhost:8000` の Django サーバーに接続します。必要に応じて `.env.local` に `NEXT_PUBLIC_DJANGO_BASE_URL` を設定してください。

```bash
NEXT_PUBLIC_DJANGO_BASE_URL=http://localhost:8000
```

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

Next.js の API Routes 経由で Django のセッション Cookie を共有しています。ログインや投稿などの操作は `/spots/api/...` にプロキシされます。
