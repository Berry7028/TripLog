import Link from 'next/link';

import ProfileForm from '@/components/ProfileForm';
import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchProfile } from '@/lib/server-api';

export default async function ProfilePage() {
  const auth = await fetchAuthStatus();
  if (!auth.is_authenticated) {
    return (
      <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <p className="text-lg font-semibold text-slate-900">プロフィールを確認するにはログインしてください。</p>
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

  const profile = await fetchProfile();

  return (
    <div className="space-y-6">
      <ProfileForm profile={profile.profile} />
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">お気に入りスポット</h2>
        <SpotGrid spots={profile.profile.favorite_spots} />
      </section>
    </div>
  );
}
