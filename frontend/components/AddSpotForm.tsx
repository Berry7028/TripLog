'use client';

import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

interface AddSpotFormProps {}

export default function AddSpotForm(_: AddSpotFormProps) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);
    const form = event.currentTarget;
    const formData = new FormData(form);

    const response = await fetch('/api/spots/add', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const detail = await response.json();
      const errorMessage = detail.error || Object.values(detail.errors || {})[0]?.[0];
      setError(errorMessage || 'スポットを投稿できませんでした。');
    } else {
      const json = await response.json();
      const spotId = json?.spot?.id;
      if (spotId) {
        router.push(`/spots/${spotId}`);
      } else {
        router.push('/');
      }
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h1 className="text-xl font-semibold text-slate-900">スポットを投稿する</h1>
      {error ? <p className="text-sm text-rose-500">{error}</p> : null}
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          スポット名
          <input name="title" required className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          住所
          <input name="address" className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          緯度
          <input name="latitude" type="number" step="any" required className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          経度
          <input name="longitude" type="number" step="any" required className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
      </div>
      <label className="flex flex-col gap-2 text-sm text-slate-600">
        説明
        <textarea name="description" rows={4} required className="rounded-2xl border border-slate-300 px-3 py-2" />
      </label>
      <label className="flex flex-col gap-2 text-sm text-slate-600">
        タグ（カンマ区切り）
        <input name="tags_text" className="rounded-2xl border border-slate-300 px-3 py-2" />
      </label>
      <div className="grid gap-4 md:grid-cols-2">
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          画像ファイル
          <input name="image" type="file" accept="image/*" className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          画像URL
          <input name="image_url" type="url" className="rounded-2xl border border-slate-300 px-3 py-2" />
        </label>
      </div>
      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white"
      >
        投稿する
      </button>
    </form>
  );
}
