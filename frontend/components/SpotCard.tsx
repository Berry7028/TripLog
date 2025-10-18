import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface SpotCardProps {
  spot: SpotSummary;
  showRecommendBadge?: boolean;
}

export default function SpotCard({ spot, showRecommendBadge }: SpotCardProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-slate-100">
        {spot.image ? (
          <Image
            src={spot.image}
            alt={spot.title}
            fill
            className="object-cover"
            sizes="(max-width:768px) 100vw, 33vw"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-slate-400">
            <span className="text-sm">No Image</span>
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-900">{spot.title}</h3>
          {showRecommendBadge && spot.is_recommended ? (
            <span className="rounded-full bg-amber-200 px-2 py-1 text-xs font-semibold text-amber-800">AIおすすめ</span>
          ) : null}
        </div>
        <p className="text-sm text-slate-600">
          {spot.description.length > 120
            ? `${spot.description.slice(0, 120)}…`
            : spot.description}
        </p>
        {spot.tags.length > 0 ? (
          <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
            {spot.tags.map((tag) => (
              <span key={tag} className="rounded-full bg-slate-100 px-2 py-1">
                #{tag}
              </span>
            ))}
          </div>
        ) : null}
        <div className="mt-auto flex items-center justify-between text-xs text-slate-500">
          {spot.address ? (
            <span className="truncate" title={spot.address}>
              {spot.address}
            </span>
          ) : (
            <span>投稿者: {spot.created_by}</span>
          )}
          <Link
            href={`/spots/${spot.id}`}
            className="rounded-full bg-primary px-3 py-1 text-xs font-semibold text-white transition hover:bg-blue-600"
          >
            詳細へ
          </Link>
        </div>
      </div>
    </div>
  );
}
