import type { SpotSummary } from '@/types/api';

import SpotCard from './SpotCard';

interface SpotGridProps {
  spots: SpotSummary[];
  sortMode?: 'recent' | 'relevance';
}

export default function SpotGrid({ spots, sortMode }: SpotGridProps) {
  if (spots.length === 0) {
    return (
      <div className="text-center py-5 text-muted bg-white border rounded-3">
        まだスポットが投稿されていません。
      </div>
    );
  }

  return (
    <div className="row g-4">
      {spots.map((spot) => (
        <div key={spot.id} className="col-12 col-sm-6 col-md-4">
          <SpotCard spot={spot} showRecommendBadge={sortMode === 'relevance'} />
        </div>
      ))}
    </div>
  );
}
