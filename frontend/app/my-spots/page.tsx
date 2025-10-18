import Link from 'next/link';

import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchMySpots } from '@/lib/server-api';

export default async function MySpotsPage() {
  const auth = await fetchAuthStatus();
  if (!auth.is_authenticated) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-lg font-semibold text-slate-900">マイスポットを表示するにはログインしてください。</p>
        <div className="mt-4 flex justify-center gap-4">
          <Link href="/login" className="rounded-full bg-primary px-4 py-2 text-white">
            ログイン
          </Link>
          <Link href="/register" className="rounded-full border border-slate-300 px-4 py-2 text-slate-600">
            新規登録
          </Link>
        </div>
      </div>
    );
  }

  const { spots } = await fetchMySpots();

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-slate-900">あなたの投稿</h1>
        <Link href="/spots/add" className="rounded-full bg-primary px-4 py-2 text-white">
          新しいスポットを投稿
        </Link>
      </header>
      <SpotGrid spots={spots} />
    </div>
  );
}
