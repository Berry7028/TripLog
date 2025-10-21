# UI 差分監査レポート（Django ➜ Next.js）

## 1. グローバルレイアウト / テーマ
- **レイアウト幅**: Django の `container` (Bootstrap) は 100%/最大 1140px。Next.js は `max-w-7xl` (1280px) + `px-4` により横幅と余白が微差。  
- **タイポグラフィ**: フォント/字間は `globals.css` で再現済み。ただし一部コンポーネントで Tailwind 標準のフォントサイズや色が使用され、Bootstrap デフォルト値と差が出る箇所あり。  
- **ボタン/フォーム半径**: Django は Bootstrap 標準 + `style.css` の `border-radius: 12px`。Next.js 側は `rounded-2xl`（約16px）や `rounded-full` を使用し、角丸量が完全一致していない。  
- **トークン管理**: CSS 変数は抽出済みだが Tailwind のユーティリティで直接 16 進数指定している箇所が散見され、デザイントークン未統一。  

## 2. ヘッダー / ナビゲーション
- **挙動**: ハンバーガーメニュー、検索フォーム、ログイン状態による表示切替は再現済み。  
- **視覚差分**: Next.js 側で `navbar` collapse 表示時に背景が白のまま（Django では navbar 色のまま）。メニュー展開時の余白・罫線も Bootstrap 標準と差分。  

## 3. ホーム（`/`）
- **カードグリッド**: Django は Bootstrap グリッド。Next.js は CSS グリッド (`grid gap-6`). 画面幅によるカラム数・ギャップが若干異なる（sm=2, xl=3 固定）。  
- **AIおすすめバッジ**: 表示ロジックは一致。ただし Django は `badge bg-warning`、Next.js は同クラスを用いつつも Tailwind ベースの余白で微差。  
- **検索結果メッセージ**: 表示内容は一致。Next.js で `alert alert-info` に加えて `bg-blue-100` などを併用しており色味が僅かに薄い。  
- **空状態**: Django は大きなアイコンと CTA ボタンを表示。Next.js は枠線付きボックスのみで、アイコンと CTA が欠落。  

## 4. マップ（`/map`）
- **ビジュアル**: `map-frame` / `details-surface` を Next.js 側でも採用し、背景色・角丸を Django と合わせ済み。  
- **最近のスポット**: Django はリンクリストを表示。Next.js も `list-group` 形式に揃え済み（ホバー時に地図だけハイライト）。  
- **Leaflet マップ**: 初期中心とズーム（東京・zoom=10）を Django に合わせた。  
- **アクセシビリティ**: サイドバー `select` などは Bootstrap クラスに戻したが、全体的な `aria` 補強は継続課題。  

## 5. スポット詳細（`/spots/[id]`）
- **画像表示**: Django は高さ 400px 固定。Next.js は `style` で同等。  
- **お気に入り/共有**: 機能・メッセージは一致。  
- **レビュー一覧**: Django では星アイコン + 件数。Next.js では `ReviewList` で `avgRating` スター表示するが CSS クラスが若干異なる。  
- **関連スポット**: Django は `list-group`. Next.js は単純リンク + ブレーク。「投稿日」フォーマットが Next で長月/日 (例: 2024年9月1日) となり整形が異なる。  

## 6. 追加フォーム（`/spots/add`）
- Leaflet 地図選択、検索/現在地ボタン、画像アップロード・URLプレビュー、フィールド単位エラー表示、キャンセルボタンを Next.js へ移植済み。  
- **差分**: Tailwind 由来の角丸や余白が一部残存。Leaflet 検索は Nominatim 依存でレート制限時のリトライUIが未提供。  

## 7. マイスポット（`/my-spots`）
- ページネーション UI を復元（1ページ 12 件、Bootstrap スタイル）。  
- 統計カードは `fetchAuthStatus().stats` を使用してレビュー数・登録日を連携済み。  
- **差分**: カードのレビュー星表示が Django と同一ではない（レビュー件数バッジ未実装）。  

## 8. プロフィール（`/profile`）
- **フォーム構造**: Django は Bootstrap ベースで 2 カラム。Next.js は `ProfileForm` 内で Tailwind へ置換。見た目が大きく異なる（枠線/背景色/角丸）。  
- **バリデーション/メッセージ**: Django は `form.errors` を各フィールドに表示。Next.js は単一エラーバナーのみ。  
- **画像プレビュー**: Django は既存画像差し替え＋ FileReader で `img` を更新。Next.js は `URL.createObjectURL` を使用し機能は同等。  
- **最近の活動**: Django は `user.spot_set` & `review_set` をテンプレートで直接使用。Next.js は API 結果（3件）を表示し、空状態メッセージは一致。  

## 9. ランキング（`/ranking`）
- 概ね一致。ただし Next.js では `Image` コンポーネント採用で角丸 / 余白が微差。  
- 週次集計タイムスタンプの表記（`toLocaleString`）が Django の `timesince` と異なるため、ヘッダー表示が増加。  

## 10. プラン（`/plan`）
- UI/挙動はほぼ一致。Next.js は `allowFullScreen` 属性小文字など細部違い。  
- ボタン `btn-outline-*` の padding が Tailwind 由来で若干異なる。  

## 11. 認証（`/login`, `/register`）
- 見た目は大部分一致。Next.js でエラー表示が `alert alert-danger` のみでフィールドハイライト無し。  
- Django フォームのヘルプテキスト (`form_text`) を Next.js では手動で複製済み。  

## 12. 管理ダッシュボード（`/manage/**`）
- `/manage` ダッシュボードを Next.js 上に移植し、`admin.css` をベースに共通レイアウト・指標カードを再現。  
- **未着手**: スポット/レビュー/タグ/ユーザー/グループ/プロフィール/閲覧ログ/AI 推薦の各 CRUD 画面は未移植。  
- API はダッシュボード向け JSON を新設済み（`/api/admin/dashboard/`）。他画面用のエンドポイント整備が必要。  

## 13. アクセシビリティ / キーボード操作
- Django + Bootstrap はデフォルトでフォーカスリングが確保される。Next.js/Tailwind 実装で `focus:outline-none` が混在し、フォーカス可視性が低い箇所あり（検索セレクト、マップフィルタなど）。  
- `aria-label`, `role` 等が Django 版より減少している部分があり（お気に入りアイコン等）。  

## 14. レスポンシブ動作
- ナビゲーションは概ね一致。ただし Next.js の `collapse` 表示で `navbar-collapse` に `width:100%` を付与しているため、Bootstrap 標準のアニメーションがなく即表示。  
- マップページのサイドバーは Tailwind で縦並び時の余白が増減。  
- Add Spot フォームでは Django 版に存在する `col-md-6` 分割が Next.js では `md:grid-cols-2` だがモバイル時の入力余白が異なる。  

---

### 優先是正項目（差分クリティカル度順）
1. **`/manage` 配下 CRUD 画面の移植**（スポット/タグ/レビュー/ユーザー等）。  
2. **グローバルトークン統一**（Tailwind 直書きの 16 進値・角丸の整理）。  
3. **SpotGrid 空状態のUI再現**（ホームでのアイコン + CTA 復元）。  
4. **レビュー星バッジの整合**（MySpots/Detailでの件数表示）。  
5. **フォーカスリング・ARIA 属性復元**（a11y 観点の差分）。  
