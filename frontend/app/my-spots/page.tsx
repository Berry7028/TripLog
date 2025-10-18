import Link from 'next/link';

import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchMySpots } from '@/lib/server-api';

function formatJoinedMonth(dateString?: string | null) {
  if (!dateString) {
    return '-';
  }
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return '-';
  }
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${year}年${month}月`;
}

export default async function MySpotsPage() {
  const auth = await fetchAuthStatus();
  if (!auth.is_authenticated) {
    return (
      <div className="text-center py-5">
        <i className="fas fa-map-marked-alt fa-5x text-muted mb-3"></i>
        <h3>マイスポットを表示するにはログインしてください</h3>
        <div className="mt-4">
          <Link href="/login" className="btn btn-primary me-2">
            ログイン
          </Link>
          <Link href="/register" className="btn btn-outline-secondary">
            新規登録
          </Link>
        </div>
      </div>
    );
  }

  const { spots } = await fetchMySpots();
  const spotCount = auth.stats?.spot_count ?? spots.length;
  const reviewCount = auth.stats?.review_count ?? 0;
  const joinedLabel = formatJoinedMonth(auth.user?.date_joined);

  return (
    <div className="row">
      <div className="col-12">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h1>
            <i className="fas fa-user me-2"></i>
            {auth.user?.username}さんの投稿
          </h1>
          <Link href="/spots/add" className="btn btn-primary">
            <i className="fas fa-plus me-2"></i>新しいスポットを投稿
          </Link>
        </div>

        {spots && spots.length > 0 ? (
          <SpotGrid spots={spots} />
        ) : (
          <div className="text-center py-5">
            <i className="fas fa-map-marked-alt fa-5x text-muted mb-3"></i>
            <h3>まだスポットを投稿していません</h3>
            <p className="text-muted">最初のスポットを投稿してみませんか？</p>
            <Link href="/spots/add" className="btn btn-primary">
              <i className="fas fa-plus me-2"></i>スポットを投稿する
            </Link>
          </div>
        )}
      </div>

      <div className="row mt-5">
        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <i className="fas fa-map-marked-alt fa-2x text-primary mb-2"></i>
              <h4>{spotCount}</h4>
              <p className="text-muted">投稿したスポット</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <i className="fas fa-star fa-2x text-warning mb-2"></i>
              <h4>{reviewCount}</h4>
              <p className="text-muted">投稿したレビュー</p>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card text-center">
            <div className="card-body">
              <i className="fas fa-calendar fa-2x text-success mb-2"></i>
              <h4>{joinedLabel}</h4>
              <p className="text-muted">登録日</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
