import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface SpotCardProps {
  spot: SpotSummary;
  showRecommendBadge?: boolean;
}

export default function SpotCard({ spot, showRecommendBadge }: SpotCardProps) {
  return (
    <div className="card-hover flex h-full flex-col overflow-hidden bg-gray-100 shadow-md" style={{ borderRadius: '22px', border: 'none' }}>
      <div className="relative aspect-[4/3] w-full overflow-hidden" style={{ height: '200px', backgroundColor: 'var(--light-gray)' }}>
        {spot.image ? (
          <Image
            src={spot.image}
            alt={spot.title}
            fill
            className="object-cover"
            sizes="(max-width:768px) 100vw, 33vw"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-gray-400">
            <i className="fas fa-image fa-3x"></i>
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4" style={{ backgroundColor: 'var(--light-gray)' }}>
        <h3 className="text-xl font-semibold text-gray-900 mb-1">{spot.title}</h3>
        {showRecommendBadge && spot.is_recommended ? (
          <span className="self-start mb-2 rounded-sm bg-yellow-400 px-2 py-1 text-xs font-semibold text-gray-900">AIおすすめ</span>
        ) : null}
        <p className="text-sm text-gray-800 mb-2 leading-relaxed">
          {spot.description.length > 70
            ? `${spot.description.slice(0, 70)}…`
            : spot.description}
        </p>
        {spot.tags.length > 0 ? (
          <div className="mb-2 flex flex-wrap gap-1">
            {spot.tags.map((tag) => (
              <span key={tag} className="rounded-sm bg-white border border-gray-300 px-2 py-1 text-xs text-gray-700">
                #{tag}
              </span>
            ))}
          </div>
        ) : null}
        <div className="mt-auto flex items-center justify-between text-xs">
          {spot.address ? (
            <small className="text-gray-600 truncate">
              <i className="fas fa-map-marker-alt me-1"></i>
              {spot.address}
            </small>
          ) : (
            <small className="text-gray-600">投稿者: {spot.created_by}</small>
          )}
          <Link
            href={`/spots/${spot.id}`}
            className="btn-detail inline-block"
          >
            詳細
          </Link>
        </div>
      </div>
    </div>
  );
}
