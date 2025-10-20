'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { ChangeEvent, FormEvent, useEffect, useState } from 'react';

import type { ProfileResponse } from '@/types/api';
import { ensureCsrfToken } from '@/lib/csrf';

interface ProfileFormProps {
  profile: ProfileResponse['profile'];
  user: ProfileResponse['user'];
}

export default function ProfileForm({ profile, user }: ProfileFormProps) {
  const router = useRouter();
  const [bio, setBio] = useState(profile.bio);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(profile.avatar);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  useEffect(() => {
    ensureCsrfToken()
      .then((token) => {
        if (token) {
          setCsrfToken(token);
        }
      })
      .catch(() => {
        // noop: フォーム送信時にエラーメッセージを表示する
      });
  }, []);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setAvatarFile(file);
    if (file) {
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const token = await ensureCsrfToken();
    if (!token) {
      setError('セキュリティトークンを取得できませんでした。ページを再読み込みしてください。');
      setIsSubmitting(false);
      return;
    }
    setCsrfToken(token);
    setIsSubmitting(true);
    setError(null);

    const formData = new FormData();
    formData.set('bio', bio);
    if (avatarFile) {
      formData.set('avatar', avatarFile);
    }
    formData.set('csrfmiddlewaretoken', token);

    const response = await fetch('/api/profile/update', {
      method: 'POST',
      body: formData,
      headers: {
        'X-CSRFToken': token,
      },
    });

    if (!response.ok) {
      const detail = await response.json();
      const errors = detail.errors as Record<string, string[]> | undefined;
      const firstError = errors ? Object.values(errors)[0]?.[0] : null;
      const errorMessage = detail.error || firstError;
      setError(errorMessage || 'プロフィールを更新できませんでした。');
    } else {
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <header className="space-y-1">
        <h2 className="text-lg font-semibold text-slate-900">プロフィール設定</h2>
        <p className="text-sm text-slate-500">ユーザー情報と自己紹介を更新できます。</p>
      </header>
      {error ? <p className="text-sm text-rose-500">{error}</p> : null}
      <div className="grid gap-6 md:grid-cols-[auto,1fr]">
        <div className="flex flex-col items-center gap-3">
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
          <label className="flex w-full flex-col items-center gap-2 text-xs text-slate-500">
            <span>アバター画像を選択</span>
            <input type="file" accept="image/*" onChange={handleFileChange} className="w-full text-xs" />
          </label>
        </div>
        <div className="flex flex-col gap-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <label className="flex flex-col gap-2 text-sm text-slate-600">
              ユーザー名
              <input
                type="text"
                value={user.username}
                disabled
                className="rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-600"
              />
              <span className="text-xs text-slate-400">ユーザー名は変更できません。</span>
            </label>
            <label className="flex flex-col gap-2 text-sm text-slate-600">
              メールアドレス
              <input
                type="email"
                value={user.email || '未設定'}
                disabled
                className="rounded-2xl border border-slate-300 bg-slate-50 px-3 py-2 text-slate-600"
              />
              <span className="text-xs text-slate-400">変更が必要な場合は管理者にご連絡ください。</span>
            </label>
          </div>
          <label className="flex flex-col gap-2 text-sm text-slate-600">
            自己紹介
            <textarea
              value={bio}
              onChange={(event) => setBio(event.target.value)}
              rows={4}
              className="rounded-2xl border border-slate-300 px-3 py-2"
            />
            <span className="text-xs text-slate-400">旅行の好みやおすすめのスポットについて共有しましょう。</span>
          </label>
        </div>
      </div>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
        <Link
          href="/my-spots"
          className="inline-flex items-center justify-center rounded-full border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100"
        >
          マイページに戻る
        </Link>
        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-70"
        >
          {isSubmitting ? '更新中...' : '保存する'}
        </button>
      </div>
    </form>
  );
}
