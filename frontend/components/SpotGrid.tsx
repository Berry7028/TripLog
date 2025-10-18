import type { SpotSummary } from '@/types/api';

import SpotCard from './SpotCard';

interface SpotGridProps {
  spots: SpotSummary[];
  sortMode?: 'recent' | 'relevance';
}

export default function SpotGrid({ spots, sortMode }: SpotGridProps) {
  if (spots.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
        まだスポットが投稿されていません。
      </div>
    );
  }

  return (
    <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-3">
      {spots.map((spot) => (
        <SpotCard key={spot.id} spot={spot} showRecommendBadge={sortMode === 'relevance'} />
      ))}
    </div>
  );
}
