'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

export default function RegisterPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password1, setPassword1] = useState('');
  const [password2, setPassword2] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (password1 !== password2) {
      setError('パスワードが一致しません。');
      return;
    }
    setIsSubmitting(true);
    setError(null);

    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password1, password2 }),
    });

    if (!response.ok) {
      const detail = await response.json();
      const errorMessage = detail.error || Object.values(detail.errors || {})[0]?.[0];
      setError(errorMessage || '登録に失敗しました。');
    } else {
      router.push('/');
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <div className="mx-auto w-full max-w-md space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-xl font-semibold text-slate-900">新規登録</h1>
      {error ? <p className="text-sm text-rose-500">{error}</p> : null}
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          ユーザー名
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
            className="rounded-2xl border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          パスワード
          <input
            type="password"
            value={password1}
            onChange={(event) => setPassword1(event.target.value)}
            required
            className="rounded-2xl border border-slate-300 px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-2 text-sm text-slate-600">
          パスワード（確認）
          <input
            type="password"
            value={password2}
            onChange={(event) => setPassword2(event.target.value)}
            required
            className="rounded-2xl border border-slate-300 px-3 py-2"
          />
        </label>
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          登録
        </button>
      </form>
      <p className="text-sm text-slate-500">
        すでにアカウントをお持ちの方は{' '}
        <Link href="/login" className="text-primary">
          ログイン
        </Link>
        へ
      </p>
    </div>
  );
}
