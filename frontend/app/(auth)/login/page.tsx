'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const detail = await response.json();
      setError(detail.error || 'ログインに失敗しました。');
    } else {
      router.push('/');
      router.refresh();
    }

    setIsSubmitting(false);
  };

  return (
    <div className="mx-auto w-full max-w-md space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
      <h1 className="text-xl font-semibold text-slate-900">ログイン</h1>
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
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            className="rounded-2xl border border-slate-300 px-3 py-2"
          />
        </label>
        <button
          type="submit"
          disabled={isSubmitting}
          className="w-full rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white"
        >
          ログイン
        </button>
      </form>
      <p className="text-sm text-slate-500">
        アカウントをお持ちでない方は{' '}
        <Link href="/register" className="text-primary">
          新規登録
        </Link>
        へ
      </p>
    </div>
  );
}
