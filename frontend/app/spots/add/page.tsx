import Link from 'next/link';

import AddSpotForm from '@/components/AddSpotForm';
import { fetchAuthStatus } from '@/lib/server-api';

export default async function AddSpotPage() {
  const auth = await fetchAuthStatus();

  if (!auth.is_authenticated) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-lg font-semibold text-slate-900">スポットを投稿するにはログインが必要です。</p>
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

  return <AddSpotForm />;
}
