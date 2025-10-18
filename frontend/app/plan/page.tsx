'use client';

import { useState } from 'react';

export default function PlanPage() {
  const [iframeKey, setIframeKey] = useState(0);

  const refreshIframe = () => {
    setIframeKey((prev) => prev + 1);
  };

  const openInNewTab = () => {
    window.open('https://maps-planner.vercel.app/', '_blank', 'noopener,noreferrer');
  };

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <div className="d-flex gap-2 ms-auto">
            <button className="btn btn-outline-primary btn-sm" onClick={refreshIframe}>
              <i className="fas fa-sync-alt me-1"></i>更新
            </button>
            <button className="btn btn-outline-secondary btn-sm" onClick={openInNewTab}>
              <i className="fas fa-external-link-alt me-1"></i>新しいタブで開く
            </button>
          </div>
        </div>

        <div className="card shadow-sm">
          <div className="card-body p-0">
            <div className="iframe-fullwidth-container">
              <iframe
                key={iframeKey}
                id="planIframe"
                src="https://maps-planner.vercel.app/"
                title="プランニングツール"
                loading="eager"
                allowFullScreen
                style={{
                  display: 'block',
                  width: '100vw',
                  minWidth: '100vw',
                  maxWidth: '100vw',
                  height: '80vh',
                  minHeight: '600px',
                  marginLeft: 'calc(-50vw + 50%)',
                  border: 'none',
                  borderRadius: 0,
                }}
              >
                <p>お使いのブラウザはiframeをサポートしていません。</p>
              </iframe>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
        .iframe-fullwidth-container {
          width: 100vw;
          height: auto;
          margin-left: calc(-50vw + 50%);
          position: relative;
          overflow: hidden;
          border-radius: 0;
        }
        @media (max-width: 768px) {
          .iframe-fullwidth-container iframe {
            height: 70vh !important;
            min-height: 500px !important;
          }
        }
        @media (max-width: 576px) {
          .iframe-fullwidth-container iframe {
            height: 60vh !important;
            min-height: 400px !important;
          }
        }
      `}</style>
    </div>
  );
}
