/**
 * TripLog Documentation - Main JavaScript
 * 共通の機能を提供するJavaScriptファイル
 */

class TripLogDocs {
    constructor() {
        this.init();
    }

    init() {
        this.setupScrollEffects();
        this.setupNavigation();
        this.setupCodeCopy();
        this.setupColorPicker();
        this.setupSearch();
        this.setupThemeToggle();
        this.setupAnalytics();
    }

    /**
     * スクロール効果の設定
     */
    setupScrollEffects() {
        // スクロールトップボタン
        const scrollTopBtn = document.getElementById('scrollTop');
        if (scrollTopBtn) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 300) {
                    scrollTopBtn.classList.remove('opacity-0', 'pointer-events-none');
                    scrollTopBtn.classList.add('opacity-100');
                } else {
                    scrollTopBtn.classList.add('opacity-0', 'pointer-events-none');
                    scrollTopBtn.classList.remove('opacity-100');
                }
            });

            scrollTopBtn.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }

        // スムーズスクロール
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // ヘッダーの背景変更
        const header = document.querySelector('nav');
        if (header) {
            window.addEventListener('scroll', () => {
                if (window.scrollY > 50) {
                    header.classList.add('backdrop-blur-md', 'bg-black/20');
                } else {
                    header.classList.remove('backdrop-blur-md', 'bg-black/20');
                }
            });
        }
    }

    /**
     * ナビゲーションの設定
     */
    setupNavigation() {
        // モバイルメニュー
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileMenu = document.getElementById('mobileMenu');

        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
            });
        }

        // アクティブなナビゲーション項目の設定
        const currentPath = window.location.pathname;
        document.querySelectorAll('nav a').forEach(link => {
            if (link.getAttribute('href') === currentPath) {
                link.classList.add('text-pink-200');
                link.classList.remove('text-white');
            }
        });
    }

    /**
     * コードコピー機能
     */
    setupCodeCopy() {
        document.querySelectorAll('pre code').forEach((block) => {
            // コピー用のブロックでなければ処理をスキップ
            if (block.closest('.no-copy')) return;

            block.addEventListener('click', () => {
                this.copyToClipboard(block.textContent);

                this.showNotification('クリップボードにコピーしました', 'success');
            });

            // ホバー効果
            block.addEventListener('mouseenter', () => {
                block.style.cursor = 'pointer';
            });
        });
    }

    /**
     * カラーコピー機能
     */
    setupColorPicker() {
        document.querySelectorAll('.color-swatch').forEach(swatch => {
            swatch.addEventListener('click', () => {
                const color = window.getComputedStyle(swatch).backgroundColor;
                const hexColor = this.rgbToHex(color);

                this.copyToClipboard(hexColor);
                this.showNotification(`色コード ${hexColor} をコピーしました`, 'success');
            });
        });
    }

    /**
     * 検索機能
     */
    setupSearch() {
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');

        if (searchInput && searchResults) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                this.performSearch(query, searchResults);
            });
        }
    }

    /**
     * テーマ切り替え
     */
    setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            // 現在のテーマを取得
            const currentTheme = localStorage.getItem('theme') || 'light';

            if (currentTheme === 'dark') {
                document.documentElement.classList.add('dark');
            }

            themeToggle.addEventListener('click', () => {
                document.documentElement.classList.toggle('dark');

                const isDark = document.documentElement.classList.contains('dark');
                localStorage.setItem('theme', isDark ? 'dark' : 'light');

                this.showNotification(
                    `テーマを${isDark ? 'ダーク' : 'ライト'}モードに変更しました`,
                    'info'
                );
            });
        }
    }

    /**
     * アナリティクスの設定
     */
    setupAnalytics() {
        // ページビューのトラッキング
        this.trackPageView();

        // スクロールトラッキング
        this.trackScrollDepth();
    }

    /**
     * 検索実行
     */
    performSearch(query, resultsContainer) {
        if (query.length < 2) {
            resultsContainer.innerHTML = '';
            return;
        }

        const searchableContent = [
            { title: 'プロジェクト概要', url: '#overview', type: 'section' },
            { title: '機能詳細', url: '#features', type: 'section' },
            { title: 'APIリファレンス', url: '#api', type: 'section' },
            { title: 'UIガイドライン', url: '#ui', type: 'section' },
            { title: 'スポット一覧取得 API', url: '#', type: 'api' },
            { title: 'スポット追加 API', url: '#', type: 'api' },
            { title: '検索 API', url: '#', type: 'api' },
        ];

        const results = searchableContent.filter(item =>
            item.title.toLowerCase().includes(query)
        );

        this.displaySearchResults(results, resultsContainer);
    }

    /**
     * 検索結果の表示
     */
    displaySearchResults(results, container) {
        if (results.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-sm">検索結果が見つかりません</p>';
            return;
        }

        const html = results.map(result => `
            <div class="p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                <h4 class="font-semibold text-gray-800">${result.title}</h4>
                <p class="text-sm text-gray-500">${result.type}</p>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * クリップボードへのコピー
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
        } catch (err) {
            // フォールバック: 従来の方法
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
        }
    }

    /**
     * 通知の表示
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type === 'success' ? 'bg-green-500' : 'bg-blue-500'}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    /**
     * RGBからHexへの変換
     */
    rgbToHex(rgb) {
        const match = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
        if (!match) return rgb;

        const r = parseInt(match[1]);
        const g = parseInt(match[2]);
        const b = parseInt(match[3]);

        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
    }

    /**
     * ページビュートラッキング
     */
    trackPageView() {
        if (typeof gtag !== 'undefined') {
            gtag('config', 'GA_MEASUREMENT_ID', {
                page_title: document.title,
                page_location: window.location.href
            });
        }
    }

    /**
     * スクロール深さトラッキング
     */
    trackScrollDepth() {
        let maxScroll = 0;
        const trackPoints = [25, 50, 75, 100];

        window.addEventListener('scroll', () => {
            const scrollPercentage = Math.round(
                (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
            );

            if (scrollPercentage > maxScroll) {
                maxScroll = scrollPercentage;

                trackPoints.forEach(point => {
                    if (scrollPercentage >= point && !this.trackedPoints.includes(point)) {
                        this.trackedPoints.push(point);
                        // トラッキングイベント送信
                        if (typeof gtag !== 'undefined') {
                            gtag('event', 'scroll_depth', {
                                event_category: 'engagement',
                                event_label: `${point}%`,
                                value: point
                            });
                        }
                    }
                });
            }
        });
    }
}

// 初期化
document.addEventListener('DOMContentLoaded', () => {
    new TripLogDocs();
});

// ユーティリティ関数
const utils = {
    // デバウンス関数
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // スロットル関数
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        }
    }
};

// グローバルオブジェクトに追加
window.TripLogDocs = TripLogDocs;
window.utils = utils;
