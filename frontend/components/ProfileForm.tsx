'use client';

import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useState } from 'react';

import type { ProfileResponse } from '@/types/api';

interface ProfileFormProps {
  profile: ProfileResponse['profile'];
}

export default function ProfileForm({ profile }: ProfileFormProps) {
  const router = useRouter();
  const [bio, setBio] = useState(profile.bio);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(profile.avatar);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setAvatarFile(file);
    if (file) {
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.set('bio', bio);
    if (avatarFile) {
      formData.set('avatar', avatarFile);
    }

    const response = await fetch('/api/profile/update', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const detail = await response.json();
      const errorMessage = detail.error || Object.values(detail.errors || {})[0]?.[0];
      setError(errorMessage || 'プロフィールを更新できませんでした。');
    } else {
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-900">プロフィール</h2>
      {error ? <p className="text-sm text-rose-500">{error}</p> : null}
      <div className="flex flex-col gap-4 sm:flex-row">
        <div className="flex flex-col items-center gap-2">
          {avatarPreview ? (
            <Image
              src={avatarPreview}
              alt="avatar preview"
              width={120}
              height={120}
              className="h-28 w-28 rounded-full object-cover"
            />
          ) : (
            <div className="flex h-28 w-28 items-center justify-center rounded-full bg-slate-200 text-slate-500">
              No Avatar
            </div>
          )}
          <input type="file" accept="image/*" onChange={handleFileChange} className="text-xs" />
        </div>
        <div className="flex-1">
          <label className="flex flex-col gap-2 text-sm text-slate-600">
            自己紹介
            <textarea
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              rows={4}
              className="rounded-2xl border border-slate-300 px-3 py-2"
            />
          </label>
        </div>
      </div>
      <button
        type="submit"
        disabled={isSubmitting}
        className="rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white"
      >
        更新する
      </button>
    </form>
  );
}
