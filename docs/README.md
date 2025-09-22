# TripLog Documentation

Django製の旅行記録マップアプリケーション「TripLog」の詳細ドキュメントです。

## 📁 フォルダ構成

```
docs/
├── index.html              # メインドキュメント
├── api-reference.html      # APIリファレンス
├── ui-guidelines.html      # UIガイドライン
├── README.md              # このファイル
├── css/
│   ├── tailwind.config.js # TailwindCSS設定
│   └── custom.css         # カスタムCSS
├── js/
│   └── main.js            # 共通JavaScript
└── images/                # 画像ファイル
```

## 🚀 セットアップ方法

### 1. GitHub Pages での公開

このドキュメントはGitHub Pagesで公開することを想定して作成されています。

#### 自動デプロイ設定
1. リポジトリのSettings > Pagesで以下の設定を行います：
   - Source: `Deploy from a branch`
   - Branch: `main` (または任意のブランチ)
   - Folder: `/docs`

#### 手動デプロイ
```bash
# docsフォルダーをGitHub Pagesブランチにプッシュ
git subtree push --prefix docs origin gh-pages
```

### 2. ローカルでの閲覧

#### Python HTTPサーバー使用
```bash
cd docs
python -m http.server 8000
```
その後、http://localhost:8000 でアクセスできます。

#### Live Server拡張機能使用
VS CodeのLive Server拡張機能を使用して、`index.html`を開いてプレビューできます。

## 📖 各ドキュメントの説明

### index.html
- **概要**: プロジェクトの全体像と主要機能を紹介
- **対象者**: プロジェクトに興味がある全ての人
- **内容**:
  - プロジェクト概要
  - 技術仕様
  - 主な機能紹介
  - API概要
  - UIデザインシステムの概要
  - デプロイ情報

### api-reference.html
- **概要**: RESTful APIの詳細なリファレンス
- **対象者**: 開発者、API統合者
- **内容**:
  - APIエンドポイント一覧
  - リクエスト/レスポンス形式
  - 認証方法
  - エラーハンドリング
  - 外部スポットサービス連携ガイド（使い方）
  - 使用例（cURL）

### ui-guidelines.html
- **概要**: デザインシステムとUIガイドライン
- **対象者**: デザイナー、フロントエンド開発者
- **内容**:
  - カラーパレット
  - タイポグラフィ
  - UIコンポーネント
  - レイアウトパターン
  - レスポンシブデザイン
  - アクセシビリティ

## 🎨 デザインシステム

### 使用技術
- **CSSフレームワーク**: TailwindCSS
- **アイコンフォント**: Font Awesome 6.0
- **ウェブフォント**: Google Fonts (Mochiy Pop P One)
- **JavaScript**: Vanilla JS (ES6+)

### カラーパレット
- **Primary**: `#568F87` (Teal)
- **Primary Dark**: `#064232` (Dark Teal)
- **Accent**: `#F5BABB` (Pink)
- **Background**: `#FFF5F2` (Cream)

### フォント
- **Heading**: Mochiy Pop P One (Google Fonts)
- **Body**: System Fonts (最適な読みやすさ)

## 🔧 カスタマイズ

### TailwindCSS設定変更
`css/tailwind.config.js`を編集して、デザインシステムをカスタマイズできます。

### カスタムCSS追加
`css/custom.css`に追加のスタイルを記述できます。

### JavaScript機能拡張
`js/main.js`に機能を追加できます。モジュール構造になっているため、拡張しやすい設計です。

## 📱 レスポンシブ対応

- **Mobile**: 320px以上
- **Tablet**: 768px以上
- **Desktop**: 1024px以上
- **Large Desktop**: 1280px以上

全ページでモバイルファーストのアプローチを採用しています。

## ♿ アクセシビリティ

- **WCAG 2.1 AA準拠**を目指した設計
- キーボードナビゲーション対応
- スクリーンリーダー対応
- 十分なカラコントラスト
- フォーカス管理

## 🔍 SEO対応

- 適切なHTML構造
- メタタグの設定
- セマンティックHTML
- Open Graph対応準備済み

## 📊 アナリティクス

Google Analytics対応済み。`js/main.js`内の`trackPageView()`関数でページビューをトラッキングできます。

## 🚨 トラブルシューティング

### スタイルが適用されない場合
1. TailwindCSS CDNが読み込まれているか確認
2. カスタムCSSファイルが読み込まれているか確認
3. ブラウザのキャッシュをクリア

### JavaScriptが動作しない場合
1. JavaScriptファイルが読み込まれているか確認
2. ブラウザのコンソールでエラーを確認
3. ES6+対応のブラウザを使用

### 画像が表示されない場合
1. 画像パスが正しいか確認
2. 画像ファイルが存在するか確認

## 🤝 コントリビューション

ドキュメントの改善は以下の手順で行ってください：

1. 該当ファイルを編集
2. 変更内容をテスト
3. プルリクエストを作成
4. レビュー後にマージ

## 📄 ライセンス

このドキュメントはプロジェクト本体と同じライセンスで提供されます。

## 📞 連絡先

質問や提案がある場合は、以下の方法で連絡してください：
- GitHub Issues
- メール: contact@triplog.com
- プロジェクトURL: https://github.com/yourusername/TripLog

---

**最終更新日**: 2025年1月21日
