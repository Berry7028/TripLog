'use client';

import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

interface ReviewFormProps {
  spotId: number;
  canReview: boolean;
}

export default function ReviewForm({ spotId, canReview }: ReviewFormProps) {
  const router = useRouter();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!canReview) {
    return null;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const response = await fetch(`/api/spots/${spotId}/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ rating, comment }),
      });
      if (!response.ok) {
        const detail = await response.json();
        const errorMessage = detail.error || Object.values(detail.errors || {})[0]?.[0];
        setError(errorMessage || 'レビューを投稿できませんでした。');
      } else {
        setComment('');
        router.refresh();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="text-lg font-semibold text-slate-900">レビューを投稿する</h3>
      {error ? <p className="text-sm text-rose-500">{error}</p> : null}
      <label className="flex flex-col gap-1 text-sm text-slate-600">
        評価
        <select
          value={rating}
          onChange={(event) => setRating(Number(event.target.value))}
          className="rounded-full border border-slate-300 px-3 py-2"
        >
          {[1, 2, 3, 4, 5].map((value) => (
            <option key={value} value={value}>
              {value} ★
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm text-slate-600">
        コメント
        <textarea
          value={comment}
          onChange={(event) => setComment(event.target.value)}
          rows={3}
          required
          className="rounded-2xl border border-slate-300 px-3 py-2"
        />
      </label>
      <button
        type="submit"
        disabled={isSubmitting}
        className="self-end rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white"
      >
        投稿する
      </button>
    </form>
  );
}
