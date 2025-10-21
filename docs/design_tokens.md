# Design Tokens（旅ログまっぷ / Next.js 移植）

| トークン | CSS 変数 / Tailwind | 用途 |
| --- | --- | --- |
| ブランドティール | `--brand-teal` / `theme.colors.primary.DEFAULT` | グローバル主要カラー、ボタン、リンク |
| ブランドティール濃 | `--brand-teal-dark` / `theme.colors.primary.dark` | ホバー / テキスト強調 |
| ページ背景 | `--page-cream` / `theme.colors.background.DEFAULT` | Body 背景、カード背景 |
| パネル灰 | `--panel-gray` / `theme.colors.background.panel` | マップサイドパネル、フォーム背景 |
| アクセントピンク | `--accent-pink` / `theme.colors.accent.DEFAULT` | バッジ、CTA ボタン |
| フッター濃色 | `--footer-deep` / `theme.colors.footer` | フッター背景 |
| フォント | `fontFamily.mochiy` | 全体の見た目統一（Mochiy Pop P One） |
| 角丸（カード） | `.card { border-radius: 18px }` / `borderRadius.card` | カード共通スタイル |
| 角丸（ピル） | `.rounded-pill` / `borderRadius.pill` | バッジ・ボタン丸み |

## 運用方針
- グローバル CSS (`app/globals.css`) では、Django オリジナルの `style.css` をベースにクラスを再定義。
- Tailwind 側でのカラー直書きは禁止し、上記トークン経由で指定する。（現状の直指定箇所は順次洗い出し中）
- 新規コンポーネントは `btn`, `card`, `form-control` 等 Bootstrap 互換クラスを優先し、トークンから派生したユーティリティのみを併用する。
