import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface SpotCardProps {
  spot: SpotSummary;
  showRecommendBadge?: boolean;
}

const DESCRIPTION_LIMIT = 70;

function truncateDescription(text: string, limit: number) {
  if (text.length <= limit) {
    return text;
  }
  return `${text.slice(0, limit)}…`;
}

export default function SpotCard({ spot, showRecommendBadge }: SpotCardProps) {
  const description = truncateDescription(spot.description ?? '', DESCRIPTION_LIMIT);

  return (
    <div className="card spot-card h-100">
      {spot.image ? (
        <div className="card-img-top position-relative" style={{ height: '200px' }}>
          <Image
            src={spot.image}
            alt={spot.title}
            fill
            sizes="(max-width: 576px) 100vw, (max-width: 992px) 50vw, 33vw"
            style={{ objectFit: 'cover' }}
          />
        </div>
      ) : (
        <div className="card-img-top image-placeholder d-flex align-items-center justify-content-center">
          <i className="fas fa-image fa-3x text-muted"></i>
        </div>
      )}

      <div className="spot-info d-flex flex-column">
        <h5 className="spot-title">{spot.title}</h5>
        {showRecommendBadge && spot.is_recommended ? (
          <span className="badge bg-warning text-dark align-self-start mb-2">AIおすすめ</span>
        ) : null}
        <p className="spot-desc mb-2">{description}</p>
        {spot.tags.length > 0 ? (
          <div className="mb-2">
            {spot.tags.map((tag) => (
              <span key={tag} className="badge bg-light text-dark border me-1">
                #{tag}
              </span>
            ))}
          </div>
        ) : null}
        <div className="mt-auto d-flex align-items-center justify-content-between">
          {spot.address ? (
            <small className="text-muted">
              <i className="fas fa-map-marker-alt me-1"></i>
              {spot.address}
            </small>
          ) : (
            <small className="text-muted">投稿者: {spot.created_by}</small>
          )}
          <Link href={`/spots/${spot.id}`} className="btn btn-detail">
            詳細
          </Link>
        </div>
      </div>
    </div>
  );
}
