'use client';

import { useState } from 'react';

interface ShareButtonProps {
  url: string;
}

export default function ShareButton({ url }: ShareButtonProps) {
  const [copied, setCopied] = useState(false);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    } catch (error) {
      console.error('Failed to copy link', error);
    }
  };

  return (
    <button
      type="button"
      onClick={copyLink}
      className="rounded-full border border-slate-300 px-3 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
    >
      {copied ? 'コピーしました！' : '共有リンクをコピー'}
    </button>
  );
}
