import RankingList from '@/components/RankingList';
import { fetchRanking } from '@/lib/server-api';

export default async function RankingPage() {
  const ranking = await fetchRanking();

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold text-slate-900">直近7日間の人気スポット</h1>
        <p className="text-sm text-slate-500">集計期間開始: {new Date(ranking.week_ago).toLocaleString('ja-JP')}</p>
      </header>
      <RankingList spots={ranking.spots} />
    </div>
  );
}
