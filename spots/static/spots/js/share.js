(function (window, document) {
    'use strict';

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
                    showFeedback(feedbackEl, '共有メニューを開きました。', 'info');
                } else {
                    await copyToClipboard(shareUrl);
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

        copyButton.addEventListener('click', async function () {
            if (!copyUrl) {
                showFeedback(feedbackEl, 'コピーするURLを取得できませんでした。', 'error');
                return;
            }

            try {
                await copyToClipboard(copyUrl);
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
