import SpotMapLayout from '@/components/SpotMapLayout';
import { fetchAuthStatus, fetchRecentSpots } from '@/lib/server-api';

export default async function MapPage() {
  const [auth, recent] = await Promise.all([fetchAuthStatus(), fetchRecentSpots()]);
  const spots = recent.spots;

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">最新スポットのマップ表示</h1>
        <p className="text-sm text-slate-500">最新50件を地図上に表示しています。</p>
      </header>
      <SpotMapLayout initialSpots={spots} recentSpots={spots.slice(0, 10)} isAuthenticated={auth.is_authenticated} />
    </div>
  );
}
