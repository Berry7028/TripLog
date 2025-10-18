import dynamic from 'next/dynamic';

import SpotGrid from '@/components/SpotGrid';
import { fetchRecentSpots } from '@/lib/server-api';

const SpotMap = dynamic(() => import('@/components/SpotMap'), { ssr: false });

export default async function MapPage() {
  const { spots } = await fetchRecentSpots();

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">最新スポットのマップ表示</h1>
        <p className="text-sm text-slate-500">最新50件を地図上に表示しています。</p>
      </header>
      <SpotMap spots={spots} />
      <div>
        <h2 className="mb-4 text-xl font-semibold text-slate-900">スポット一覧</h2>
        <SpotGrid spots={spots} />
      </div>
    </div>
  );
}
