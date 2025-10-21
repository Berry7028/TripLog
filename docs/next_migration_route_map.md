# 旅ログまっぷ Next.js 移植ルートマップ

| Django URL パターン | Django テンプレート | Next.js ルート | 主担当コンポーネント / ページ | 備考 |
| --- | --- | --- | --- | --- |
| `/` / `/home/` | `spots/home.html` | `/` (`app/page.tsx`) | `SearchSortBar`, `SpotGrid`, `Pagination` | 検索・並び替え・AIレコメンドバッジ対応済み |
| `/map/` | `spots/map.html` | `/map` (`app/map/page.tsx`) | `SpotMapLayout`, `SpotMap`, `SpotMapSidebar` | Leaflet マップ + フィルタ UI |
| `/ranking/` | `spots/ranking.html` | `/ranking` (`app/ranking/page.tsx`) | `RankingList` | 週間ビュー数ランキング |
| `/plan/` | `spots/plan.html` | `/plan` (`app/plan/page.tsx`) | `PlanPage` (inline) | 外部 iframe 埋め込み・リロード & 新規タブ制御 |
| `/add/` | `spots/add_spot.html` | `/spots/add` (`app/spots/add/page.tsx`) | `AddSpotForm` | 画像アップロード / CSRF 対応フォーム |
| `/spot/<id>/` | `spots/spot_detail.html` | `/spots/[id]` (`app/spots/[id]/page.tsx`) | `FavoriteButton`, `ShareButton`, `ReviewForm`, `ReviewList`, `ViewTracker` | 関連スポット・埋め込みマップ含む詳細表示 |
| `/my-spots/` | `spots/my_spots.html` | `/my-spots` (`app/my-spots/page.tsx`) | `SpotGrid` | ログイン必須 / 空状態 UI 再現 |
| `/profile/` | `spots/profile.html` | `/profile` (`app/profile/page.tsx`) | `ProfileForm` | プロフィール更新・統計カード |
| `/register/` | `registration/register.html` | `/register` (`app/(auth)/register/page.tsx`) | `RegisterPage` | Django 標準バリデーションメッセージ反映 |
| `/login/` | `registration/login.html` | `/login` (`app/(auth)/login/page.tsx`) | `LoginPage`, `LogoutButton` | セッション連携・ゲスト案内カード |
| `/ranking/` (API) | `spots/ranking.html` | `/ranking` (同上) | `fetchRanking` (lib/server-api) | SSR ロードで Django API と連携 |
| `/manage/` | `spots/admin/dashboard.html` | `/manage` (`app/manage/page.tsx`) | `AdminSidebar`, `ManageDashboardPage` | ダッシュボード移植済み（他管理画面は引き続き実装必要） |
| `/manage/spots/` | `spots/admin/spot_list.html` | **未実装** | — | スポット管理一覧・フィルタ UI |
| `/manage/spots/add/` | `spots/admin/spot_form.html` | **未実装** | — | スポット管理フォーム |
| `/manage/spots/<id>/edit/` | `spots/admin/spot_form.html` | **未実装** | — | 〃 |
| `/manage/spots/<id>/delete/` | `spots/admin/spot_confirm_delete.html` | **未実装** | — | 削除確認モーダル/ページ |
| `/manage/tags/` ほかタグ CRUD | `spots/admin/tag_list.html` など | **未実装** | — | タグ CRUD UI |
| `/manage/reviews/` | `spots/admin/review_list.html` | **未実装** | — | レビュー管理 |
| `/manage/users/` | `spots/admin/user_list.html` | **未実装** | — | ユーザー一覧・詳細・権限操作 |
| `/manage/groups/` | `spots/admin/group_list.html` | **未実装** | — | グループ管理 |
| `/manage/profiles/` | `spots/admin/profile_list.html` | **未実装** | — | プロフィール承認/編集 |
| `/manage/spot-views/` | `spots/admin/spotview_list.html` | **未実装** | — | ビュー統計 |
| `/manage/recommendations/` 系 | `spots/admin/recommendation_dashboard.html` ほか | **未実装** | — | AI レコメンド設定/ログ/スコア管理 |

## グローバルレイアウト対応
- Django `spots/base.html` のヘッダー/フッター/Bootstrap 依存は Next.js `app/layout.tsx` + `components/Header.tsx` + `components/Footer.tsx` へ移管済み。
- CSS トークンは `app/globals.css` と `tailwind.config.js` に抽出し、Bootstrap クラス互換ユーティリティを補完。

## 今後の対応方針
1. **管理ダッシュボード群の移植**: `/manage/**` 配下の各テンプレートを Next.js App Router で構造化し、共通レイアウト（`ManageLayout` 仮称）と UI コンポーネントを整備する。
2. **UI 差分検証**: Storybook / Playwright などで Django レンダリングとの差異（余白・レスポンシブ・a11y）を自動比較する仕組みを導入。
3. **API 境界整備**: Admin 用の JSON API が未整備の部分は Django 側に REST エンドポイントを追加し、Next.js からフェッチできるようにする。
