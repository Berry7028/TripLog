(function (window, document) {
    'use strict';

    function getCookie(name) {
        if (!document.cookie) {
            return null;
        }

        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i += 1) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        return null;
    }

    function getCsrfToken() {
        return getCookie('csrftoken');
    }

    function showFeedback(feedbackEl, message, type) {
        if (!feedbackEl) {
            return;
        }
        feedbackEl.textContent = message;
        feedbackEl.classList.remove('d-none', 'alert-success', 'alert-danger', 'alert-info');
        const alertClass = type === 'error' ? 'alert-danger' : type === 'info' ? 'alert-info' : 'alert-success';
        feedbackEl.classList.add('alert', alertClass);
    }

    async function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(text);
            return true;
        }

        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.setAttribute('readonly', '');
        textarea.style.position = 'absolute';
        textarea.style.left = '-9999px';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            const successful = document.execCommand('copy');
            document.body.removeChild(textarea);
            return successful;
        } catch (err) {
            document.body.removeChild(textarea);
            throw err;
        }
    }

    async function recordShareAnalytics(endpoint, payload) {
        if (!endpoint || !payload || !payload.spot_id || !payload.method) {
            return;
        }

        const headers = {
            'Content-Type': 'application/json',
        };
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers,
                body: JSON.stringify(payload),
                credentials: 'same-origin',
            });
            if (!response.ok) {
                throw new Error('Unexpected status: ' + response.status);
            }
        } catch (error) {
            console.warn('Failed to record share analytics:', error);
        }
    }

    function initSpotShareButton() {
        const shareButton = document.getElementById('shareButton');
        if (!shareButton) {
            return;
        }

        const shareUrl = shareButton.dataset.shareUrl || window.location.href;
        const shareTitle = shareButton.dataset.shareTitle || document.title;
        const shareText = shareButton.dataset.shareText || '';
        const feedbackId = shareButton.dataset.feedbackTarget;
        const feedbackEl = feedbackId ? document.getElementById(feedbackId) : null;
        const analyticsEndpoint = shareButton.dataset.analyticsUrl || '';
        const spotId = shareButton.dataset.spotId || '';

        let isSharing = false;

        shareButton.addEventListener('click', async function () {
            if (isSharing) {
                return; // 共有処理中は無視
            }

            if (!shareUrl) {
                showFeedback(feedbackEl, '共有するURLを取得できませんでした。', 'error');
                return;
            }

            isSharing = true;
            shareButton.disabled = true;

            try {
                if (navigator.share) {
                    await navigator.share({
                        title: shareTitle,
                        text: shareText,
                        url: shareUrl,
                    });
                    await recordShareAnalytics(analyticsEndpoint, {
                        spot_id: spotId,
                        method: 'web_share',
                        share_url: shareUrl,
                    });
                    showFeedback(feedbackEl, '共有メニューを開きました。', 'info');
                } else {
                    await copyToClipboard(shareUrl);
                    await recordShareAnalytics(analyticsEndpoint, {
                        spot_id: spotId,
                        method: 'copy_link',
                        share_url: shareUrl,
                    });
                    showFeedback(feedbackEl, 'スポットのリンクをコピーしました！', 'success');
                }
            } catch (error) {
                // AbortError（ユーザーがキャンセルした場合）はエラーとみなさない
                if (error.name === 'AbortError') {
                    showFeedback(feedbackEl, '共有がキャンセルされました。', 'info');
                } else if (error.name === 'InvalidStateError') {
                    // 共有状態の競合時は何も表示せず、静かに終了
                    return;
                } else {
                    showFeedback(feedbackEl, '共有に失敗しました。お手数ですが手動でリンクをコピーしてください。', 'error');
                }
            } finally {
                isSharing = false;
                shareButton.disabled = false;
            }
        });
    }

    function initCopyUrlButton() {
        const copyButton = document.getElementById('copyUrlButton');
        if (!copyButton) {
            return;
        }

        const copyUrl = copyButton.dataset.copyUrl || window.location.href;
        const feedbackId = copyButton.dataset.feedbackTarget;
        const feedbackEl = feedbackId ? document.getElementById(feedbackId) : null;
        const analyticsEndpoint = copyButton.dataset.analyticsUrl || '';
        const spotId = copyButton.dataset.spotId || '';

        copyButton.addEventListener('click', async function () {
            if (!copyUrl) {
                showFeedback(feedbackEl, 'コピーするURLを取得できませんでした。', 'error');
                return;
            }

            try {
                await copyToClipboard(copyUrl);
                await recordShareAnalytics(analyticsEndpoint, {
                    spot_id: spotId,
                    method: 'copy_link',
                    share_url: copyUrl,
                });
                showFeedback(feedbackEl, 'スポットのリンクをコピーしました！', 'success');
            } catch (error) {
                showFeedback(feedbackEl, 'コピーに失敗しました。お手数ですが手動でリンクをコピーしてください。', 'error');
                console.error('Failed to copy URL:', error);
            }
        });
    }

    window.initSpotShareButton = initSpotShareButton;
    window.initCopyUrlButton = initCopyUrlButton;
})(window, document);
