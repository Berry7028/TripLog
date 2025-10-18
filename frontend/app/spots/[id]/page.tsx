import Image from 'next/image';
import Link from 'next/link';

import FavoriteButton from '@/components/FavoriteButton';
import ReviewForm from '@/components/ReviewForm';
import ReviewList from '@/components/ReviewList';
import ShareButton from '@/components/ShareButton';
import ViewTracker from '@/components/ViewTracker';
import { fetchSpotDetail } from '@/lib/server-api';

interface SpotDetailPageProps {
  params: { id: string };
}

export default async function SpotDetailPage({ params }: SpotDetailPageProps) {
  const spotId = Number(params.id);
  const data = await fetchSpotDetail(spotId);
  const { spot, viewer } = data;

  return (
    <div className="space-y-8">
      <ViewTracker spotId={spotId} enabled={viewer.is_authenticated} />
      <div className="grid gap-8 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm">
            <div className="relative aspect-[16/9] w-full overflow-hidden bg-slate-100">
              {spot.image ? (
                <Image src={spot.image} alt={spot.title} fill className="object-cover" />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-slate-400">画像なし</div>
              )}
            </div>
            <div className="space-y-4 p-6">
              <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <h1 className="text-2xl font-semibold text-slate-900">{spot.title}</h1>
                  <p className="text-sm text-slate-500">投稿者: {spot.created_by_detail?.username ?? '不明'}</p>
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <ShareButton url={data.share_url} />
                  {viewer.is_authenticated ? (
                    <FavoriteButton
                      spotId={spotId}
                      initialFavorite={data.is_favorite}
                      disabled={!viewer.is_authenticated}
                    />
                  ) : (
                    <Link
                      href="/login"
                      className="rounded-full border border-slate-300 px-4 py-2 text-sm text-slate-600 transition hover:bg-slate-100"
                    >
                      ログインしてお気に入り
                    </Link>
                  )}
                </div>
              </div>
              <p className="whitespace-pre-wrap text-sm text-slate-700">{spot.description}</p>
              {spot.tags.length > 0 ? (
                <div className="flex flex-wrap gap-2 text-xs text-slate-500">
                  {spot.tags.map((tag) => (
                    <span key={tag} className="rounded-full bg-slate-100 px-2 py-1">
                      #{tag}
                    </span>
                  ))}
                </div>
              ) : null}
              <div className="grid gap-2 text-sm text-slate-600 sm:grid-cols-2">
                {spot.address ? <div>住所: {spot.address}</div> : null}
                <div>
                  座標: {spot.latitude.toFixed(4)}, {spot.longitude.toFixed(4)}
                </div>
              </div>
              <div className="overflow-hidden rounded-2xl border border-slate-200">
                <iframe
                  title="map"
                  src={`https://www.openstreetmap.org/export/embed.html?bbox=${spot.longitude - 0.01}%2C${spot.latitude - 0.01}%2C${spot.longitude + 0.01}%2C${spot.latitude + 0.01}&layer=mapnik&marker=${spot.latitude}%2C${spot.longitude}`}
                  className="h-64 w-full"
                  loading="lazy"
                />
              </div>
            </div>
          </div>
          <ReviewForm spotId={spotId} canReview={viewer.is_authenticated && viewer.can_review} />
          <ReviewList reviews={data.reviews} avgRating={data.avg_rating} />
        </div>
        <aside className="space-y-6">
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">関連スポット</h2>
            {data.related_spots.length === 0 ? (
              <p className="text-sm text-slate-500">関連スポットはありません。</p>
            ) : (
              <div className="space-y-4">
                {data.related_spots.map((related) => (
                  <Link
                    key={related.id}
                    href={`/spots/${related.id}`}
                    className="block rounded-2xl border border-slate-100 p-3 transition hover:bg-slate-50"
                  >
                    <p className="font-semibold text-slate-900">{related.title}</p>
                    <p className="text-xs text-slate-500">{related.address}</p>
                  </Link>
                ))}
              </div>
            )}
          </div>
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">スポット情報</h2>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>投稿日時: {spot.created_at ? new Date(spot.created_at).toLocaleString('ja-JP') : '不明'}</li>
              <li>更新日時: {spot.updated_at ? new Date(spot.updated_at).toLocaleString('ja-JP') : '不明'}</li>
              <li>AI生成: {spot.is_ai_generated ? 'はい' : 'いいえ'}</li>
            </ul>
          </div>
        </aside>
      </div>
    </div>
  );
}
