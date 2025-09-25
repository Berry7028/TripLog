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

        shareButton.addEventListener('click', async function () {
            if (!shareUrl) {
                showFeedback(feedbackEl, '共有するURLを取得できませんでした。', 'error');
                return;
            }

            try {
                if (navigator.share) {
                    await navigator.share({
                        title: shareTitle,
                        text: shareText,
                        url: shareUrl,
                    });
                    showFeedback(feedbackEl, '共有メニューを開きました。', 'info');
                    return;
                }

                await copyToClipboard(shareUrl);
                showFeedback(feedbackEl, 'スポットのリンクをコピーしました！', 'success');
            } catch (error) {
                showFeedback(feedbackEl, '共有に失敗しました。お手数ですが手動でリンクをコピーしてください。', 'error');
                console.error('Failed to share spot link:', error);
            }
        });
    }

    window.initSpotShareButton = initSpotShareButton;
})(window, document);
