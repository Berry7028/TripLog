import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface SpotCardProps {
  spot: SpotSummary;
  showRecommendBadge?: boolean;
}

export default function SpotCard({ spot, showRecommendBadge }: SpotCardProps) {
  return (
    <div className="spot-card card-hover h-100">
      <div className="position-relative">
        {spot.image ? (
          <Image
            src={spot.image}
            alt={spot.title}
            width={400}
            height={300}
            className="card-img-top"
            style={{ objectFit: 'cover', height: '200px' }}
            sizes="(max-width: 768px) 100vw, 33vw"
          />
        ) : (
          <div className="image-placeholder d-flex align-items-center justify-content-center text-muted">
            <i className="fas fa-image fa-3x" aria-hidden="true"></i>
          </div>
        )}
      </div>
      <div className="spot-info d-flex flex-column">
        <h3 className="spot-title fw-bold text-dark">{spot.title}</h3>
        {showRecommendBadge && spot.is_recommended ? (
          <span className="badge bg-warning text-dark align-self-start mb-2">AIおすすめ</span>
        ) : null}
        <p className="spot-desc mb-2">
          {spot.description.length > 70 ? `${spot.description.slice(0, 70)}…` : spot.description}
        </p>
        {spot.tags.length > 0 ? (
          <div className="mb-2">
            {spot.tags.map((tag) => (
              <span key={tag} className="badge bg-light text-dark border me-1 mb-1">
                #{tag}
              </span>
            ))}
          </div>
        ) : null}
        <div className="mt-auto d-flex align-items-center justify-content-between">
          {spot.address ? (
            <small className="text-muted text-truncate" style={{ maxWidth: '70%' }}>
              <i className="fas fa-map-marker-alt me-1" aria-hidden="true"></i>
              {spot.address}
            </small>
          ) : (
            <small className="text-muted">投稿者: {spot.created_by}</small>
          )}
          <Link href={`/spots/${spot.id}`} className="btn-detail">
            詳細
          </Link>
        </div>
      </div>
    </div>
  );
}
