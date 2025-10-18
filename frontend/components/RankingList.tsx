import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface RankingListProps {
  spots: SpotSummary[];
}

function formatWeeklyViews(count?: number): string {
  if (typeof count !== 'number') {
    return '0 回';
  }
  return `${count.toLocaleString('ja-JP')} 回`;
}

export default function RankingList({ spots }: RankingListProps) {
  if (spots.length === 0) {
    return (
      <div className="text-center py-5">
        <i className="far fa-eye-slash fa-4x text-muted mb-3"></i>
        <p className="mb-0">直近7日間の閲覧データがありません。</p>
      </div>
    );
  }

  return (
    <div className="row g-3">
      {spots.map((spot, index) => (
        <div key={spot.id} className="col-12">
          <div className="card shadow-sm">
            <div className="card-body d-flex align-items-center">
              <div className="display-6 fw-bold me-3" style={{ width: '3rem', textAlign: 'center' }}>
                {index + 1}
              </div>
              {spot.image && (
                <Image
                  src={spot.image}
                  alt={spot.title}
                  width={72}
                  height={72}
                  className="me-3 rounded"
                  style={{ width: '72px', height: '72px', objectFit: 'cover' }}
                />
              )}
              <div className="flex-grow-1">
                <h5 className="mb-1">
                  <Link href={`/spots/${spot.id}`} className="text-decoration-none">
                    {spot.title}
                  </Link>
                </h5>
                {spot.address && (
                  <div className="text-muted small">
                    <i className="fas fa-map-marker-alt me-1"></i>
                    {spot.address}
                  </div>
                )}
                {spot.tags.length > 0 && (
                  <div className="mt-1">
                    {spot.tags.map((tag) => (
                      <span key={tag} className="badge bg-light text-dark border me-1">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div className="text-end" style={{ width: '8rem' }}>
                <div className="fw-bold">
                  <i className="far fa-eye me-1"></i>
                  {formatWeeklyViews(spot.weekly_views)}
                </div>
                <div className="text-muted small">過去7日</div>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
