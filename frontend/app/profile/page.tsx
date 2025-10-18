import Link from 'next/link';

import ProfileForm from '@/components/ProfileForm';
import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchProfile } from '@/lib/server-api';

function formatMembershipDuration(dateJoined?: string | null): string {
  if (!dateJoined) {
    return '不明';
  }
  const joined = new Date(dateJoined);
  if (Number.isNaN(joined.getTime())) {
    return '不明';
  }
  const now = new Date();
  const diffMs = now.getTime() - joined.getTime();
  if (diffMs <= 0) {
    return '1日未満';
  }

  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 60) {
    return `${Math.max(minutes, 1)}分`;
  }
  const hours = Math.floor(minutes / 60);
  if (hours < 24) {
    return `${hours}時間`;
  }
  const days = Math.floor(hours / 24);
  if (days < 30) {
    return `${days}日`;
  }
  const months = Math.floor(days / 30);
  if (months < 12) {
    return `${months}ヶ月`;
  }
  const years = Math.floor(days / 365);
  return `${years}年`;
}

export default async function ProfilePage() {
  const auth = await fetchAuthStatus();
  if (!auth.is_authenticated) {
    return (
      <div className="text-center py-5">
        <i className="fas fa-user-circle fa-5x text-muted mb-3"></i>
        <h3>プロフィールを確認するにはログインしてください</h3>
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

  const profile = await fetchProfile();
  const stats = profile.stats ?? {
    spot_count: 0,
    review_count: 0,
    favorite_count: profile.profile.favorite_spots.length,
  };
  const membershipDuration = formatMembershipDuration(profile.user.date_joined ?? auth.user?.date_joined);
  const recentSpots = profile.recent_activity?.spots ?? [];
  const recentReviews = profile.recent_activity?.reviews ?? [];

  return (
    <div className="row justify-content-center">
      <div className="col-md-8">
        <div className="card">
          <div className="card-header">
            <h2>
              <i className="fas fa-user me-2"></i>プロフィール設定
            </h2>
          </div>
          <div className="card-body">
            <ProfileForm profile={profile.profile} user={profile.user} />
          </div>
        </div>

        {/* アカウント統計 */}
        <div className="card mt-4">
          <div className="card-header">
            <h5>
              <i className="fas fa-chart-bar me-2"></i>アカウント統計
            </h5>
          </div>
          <div className="card-body">
            <div className="row text-center">
              <div className="col-md-3">
                <div className="border-end">
                  <h4 className="text-primary">{stats.spot_count}</h4>
                  <p className="text-muted mb-0">投稿スポット</p>
                </div>
              </div>
              <div className="col-md-3">
                <div className="border-end">
                  <h4 className="text-warning">{stats.review_count}</h4>
                  <p className="text-muted mb-0">投稿レビュー</p>
                </div>
              </div>
              <div className="col-md-3">
                <div className="border-end">
                  <h4 className="text-success">{stats.favorite_count}</h4>
                  <p className="text-muted mb-0">お気に入り</p>
                </div>
              </div>
              <div className="col-md-3">
                <h4 className="text-info">{membershipDuration}</h4>
                <p className="text-muted mb-0">利用期間</p>
              </div>
            </div>
          </div>
        </div>

        {/* 最近の活動 */}
        <div className="card mt-4">
          <div className="card-header">
            <h5>
              <i className="fas fa-clock me-2"></i>最近の活動
            </h5>
          </div>
          <div className="card-body">
            <h6>最近投稿したスポット</h6>
            {recentSpots.length === 0 ? (
              <p className="text-muted">まだスポットを投稿していません。</p>
            ) : (
              <>
                {recentSpots.slice(0, 3).map((spot: any) => (
                  <div key={spot.id} className="d-flex align-items-center mb-2">
                    <i className="fas fa-map-marker-alt text-primary me-2"></i>
                    <div>
                      <Link href={`/spots/${spot.id}`} className="text-decoration-none">
                        {spot.title}
                      </Link>
                      <br />
                      <small className="text-muted">
                        {spot.created_at ? new Date(spot.created_at).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }) : '日付不明'}
                      </small>
                    </div>
                  </div>
                ))}
              </>
            )}

            <h6 className="mt-3">最近投稿したレビュー</h6>
            {recentReviews.length === 0 ? (
              <p className="text-muted">まだレビューを投稿していません。</p>
            ) : (
              <>
                {recentReviews.slice(0, 3).map((review: any) => (
                  <div key={review.id} className="d-flex align-items-center mb-2">
                    <i className="fas fa-star text-warning me-2"></i>
                    <div>
                      <Link href={`/spots/${review.spot.id}`} className="text-decoration-none">
                        {review.spot.title}
                      </Link>
                      <div className="rating">
                        {Array.from({ length: 5 }).map((_, index) => (
                          <i key={index} className={index < review.rating ? 'fas fa-star' : 'far fa-star'}></i>
                        ))}
                      </div>
                      <small className="text-muted">
                        {review.created_at ? new Date(review.created_at).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }) : '日付不明'}
                      </small>
                    </div>
                  </div>
                ))}
              </>
            )}

            {recentSpots.length === 0 && recentReviews.length === 0 && (
              <p className="text-muted text-center py-3">まだ活動がありません。</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
