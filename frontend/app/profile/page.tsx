import Link from 'next/link';

import ProfileForm from '@/components/ProfileForm';
import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchProfile } from '@/lib/server-api';

function formatMembershipDuration(dateJoined?: string | null): string {
  if (!dateJoined) {
    return '不明';
  }
  const joined = new Date(dateJoined);
  if (Number.isNaN(joined.getTime())) {
    return '不明';
  }
  const now = new Date();
  const diffMs = now.getTime() - joined.getTime();
  if (diffMs <= 0) {
    return '1日未満';
  }

  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 60) {
    return `${Math.max(minutes, 1)}分`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours}時間`;
  }
  const days = Math.floor(hours / 24);
  if (days < 30) {
    return `${days}日`;
  }
  const months = Math.floor(days / 30);
  if (months < 12) {
    return `${months}ヶ月`;
  }
  const years = Math.floor(days / 365);
  return `${years}年`;
}

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
  const stats = profile.stats ?? {
    spot_count: 0,
    review_count: 0,
    favorite_count: profile.profile.favorite_spots.length,
  };
  const membershipDuration = formatMembershipDuration(profile.user.date_joined ?? auth.user?.date_joined);
  const recentSpots = profile.recent_activity?.spots ?? [];
  const recentReviews = profile.recent_activity?.reviews ?? [];

  return (
    <div className="space-y-6">
      <ProfileForm profile={profile.profile} user={profile.user} />
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">アカウント統計</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
            <p className="text-2xl font-semibold text-primary">{stats.spot_count}</p>
            <p className="text-sm text-slate-500">投稿スポット</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
            <p className="text-2xl font-semibold text-amber-500">{stats.review_count}</p>
            <p className="text-sm text-slate-500">投稿レビュー</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
            <p className="text-2xl font-semibold text-emerald-500">{stats.favorite_count}</p>
            <p className="text-sm text-slate-500">お気に入り</p>
          </div>
          <div className="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm">
            <p className="text-2xl font-semibold text-sky-500">{membershipDuration}</p>
            <p className="text-sm text-slate-500">利用期間</p>
          </div>
        </div>
      </section>
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">最近の活動</h2>
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-base font-semibold text-slate-900">最近投稿したスポット</h3>
            {recentSpots.length === 0 ? (
              <p className="text-sm text-slate-500">まだスポットを投稿していません。</p>
            ) : (
              <ul className="space-y-3">
                {recentSpots.map((spot) => (
                  <li key={spot.id} className="rounded-2xl border border-slate-100 p-3">
                    <Link href={`/spots/${spot.id}`} className="font-semibold text-primary hover:underline">
                      {spot.title}
                    </Link>
                    <p className="text-xs text-slate-500">
                      {spot.created_at ? new Date(spot.created_at).toLocaleDateString('ja-JP') : '日付不明'}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="space-y-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h3 className="text-base font-semibold text-slate-900">最近投稿したレビュー</h3>
            {recentReviews.length === 0 ? (
              <p className="text-sm text-slate-500">まだレビューを投稿していません。</p>
            ) : (
              <ul className="space-y-3">
                {recentReviews.map((review) => (
                  <li key={review.id} className="rounded-2xl border border-slate-100 p-3">
                    <Link href={`/spots/${review.spot.id}`} className="font-semibold text-primary hover:underline">
                      {review.spot.title}
                    </Link>
                    <div className="flex items-center gap-2 text-xs text-amber-500">
                      {Array.from({ length: 5 }).map((_, index) => (
                        <span key={index}>{index < review.rating ? '★' : '☆'}</span>
                      ))}
                    </div>
                    <p className="text-xs text-slate-500">
                      {review.created_at ? new Date(review.created_at).toLocaleDateString('ja-JP') : '日付不明'}
                    </p>
                    {review.comment ? (
                      <p className="mt-1 text-sm text-slate-600">{review.comment}</p>
                    ) : null}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>
      <section className="space-y-4">
        <h2 className="text-lg font-semibold text-slate-900">お気に入りスポット</h2>
        <SpotGrid spots={profile.profile.favorite_spots} />
      </section>
    </div>
  );
}
