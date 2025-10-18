import RankingList from '@/components/RankingList';
import { fetchRanking } from '@/lib/server-api';

export default async function RankingPage() {
  const ranking = await fetchRanking();

  return (
    <div>
      <div className="d-flex align-items-center mb-3">
        <h2 className="me-3">
          <i className="fas fa-trophy text-warning me-2"></i>ランキング
        </h2>
        <span className="text-muted">直近7日間の閲覧数</span>
        <div className="ms-auto small text-muted">
          集計開始: {new Date(ranking.week_ago).toLocaleString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      <RankingList spots={ranking.spots} />
    </div>
  );
}
