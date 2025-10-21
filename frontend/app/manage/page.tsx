import Link from 'next/link';

import { fetchAdminDashboard, fetchAuthStatus } from '@/lib/server-api';

function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return '-';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '-';
  }
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default async function ManageDashboardPage() {
  const auth = await fetchAuthStatus();
  if (!auth.is_authenticated) {
    return (
      <div className="admin-main">
        <header className="admin-header">
          <h1 className="admin-title">
            <i className="fas fa-lock me-2" aria-hidden="true"></i>管理ダッシュボード
          </h1>
          <p className="admin-subtitle">閲覧にはログインが必要です。</p>
        </header>
        <div className="admin-content">
          <div className="alert alert-warning" role="alert">
            スタッフ専用の画面です。ログイン後に再度アクセスしてください。
          </div>
          <div className="d-flex gap-3">
            <Link href="/login" className="btn btn-primary">
              ログインページへ
            </Link>
            <Link href="/" className="btn btn-outline-secondary">
              トップへ戻る
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!auth.user?.is_staff) {
    return (
      <div className="admin-main">
        <header className="admin-header">
          <h1 className="admin-title">
            <i className="fas fa-user-shield me-2" aria-hidden="true"></i>管理ダッシュボード
          </h1>
          <p className="admin-subtitle">管理者権限が必要です。</p>
        </header>
        <div className="admin-content">
          <div className="alert alert-danger" role="alert">
            現在のアカウントには管理者権限がありません。必要な場合は管理者にお問い合わせください。
          </div>
          <Link href="/" className="btn btn-secondary align-self-start">
            トップに戻る
          </Link>
        </div>
      </div>
    );
  }

  let dashboard: Awaited<ReturnType<typeof fetchAdminDashboard>> | null = null;
  let loadError: string | null = null;
  try {
    dashboard = await fetchAdminDashboard();
  } catch (error) {
    console.error('Failed to load admin dashboard', error);
    loadError = 'ダッシュボード情報の取得に失敗しました。時間をおいて再度お試しください。';
  }

  return (
    <>
      <header className="admin-header">
        <h1 className="admin-title">
          <i className="fas fa-chart-line me-2" aria-hidden="true"></i>
          ダッシュボード
        </h1>
        <p className="admin-subtitle">直近の状況を把握し、主要データを素早く確認できます。</p>
      </header>
      <div className="admin-content">
        {loadError ? (
          <div className="alert alert-warning" role="alert">
            {loadError}
          </div>
        ) : null}

        {dashboard ? (
          <>
            <section className="admin-metrics">
              <div className="metric-card">
                <div className="metric-icon metric-icon--spots">
                  <i className="fas fa-map-marker-alt" aria-hidden="true"></i>
                </div>
                <div className="metric-label">スポット</div>
                <div className="metric-value">{dashboard.totals.spots}</div>
                <div className="metric-footer">合計登録数</div>
              </div>
              <div className="metric-card">
                <div className="metric-icon metric-icon--reviews">
                  <i className="fas fa-comments" aria-hidden="true"></i>
                </div>
                <div className="metric-label">レビュー</div>
                <div className="metric-value">{dashboard.totals.reviews}</div>
                <div className="metric-footer">コミュニティからの声</div>
              </div>
              <div className="metric-card">
                <div className="metric-icon metric-icon--users">
                  <i className="fas fa-user-friends" aria-hidden="true"></i>
                </div>
                <div className="metric-label">ユーザー</div>
                <div className="metric-value">{dashboard.totals.users}</div>
                <div className="metric-footer">登録ユーザー数</div>
              </div>
              <div className="metric-card">
                <div className="metric-icon metric-icon--tags">
                  <i className="fas fa-tags" aria-hidden="true"></i>
                </div>
                <div className="metric-label">タグ</div>
                <div className="metric-value">{dashboard.totals.tags}</div>
                <div className="metric-footer">整理に利用されたタグ</div>
              </div>
              <div className="metric-card">
                <div className="metric-icon metric-icon--views">
                  <i className="fas fa-eye" aria-hidden="true"></i>
                </div>
                <div className="metric-label">直近7日閲覧</div>
                <div className="metric-value">{dashboard.totals.views_last_week}</div>
                <div className="metric-footer">SpotView ログ</div>
              </div>
              <div className="metric-card">
                <div className="metric-icon metric-icon--ai">
                  <i className="fas fa-robot" aria-hidden="true"></i>
                </div>
                <div className="metric-label">AIおすすめスコア</div>
                <div className="metric-value">{dashboard.totals.ai_scores}</div>
                <div className="metric-footer">
                  <Link href="/manage/recommendations" className="text-decoration-none" style={{ color: 'inherit' }}>
                    管理画面へ →
                  </Link>
                </div>
              </div>
            </section>

            <section className="admin-panels">
              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-bolt me-2" aria-hidden="true"></i>
                    最新スポット
                  </h2>
                  <Link href="/manage/spots" className="panel-link">
                    一覧を見る
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.new_spots.length ? (
                    dashboard.new_spots.map((spot) => (
                      <li key={spot.id}>
                        <span className="panel-title">{spot.title}</span>
                        <span className="panel-meta">
                          {spot.created_by} / {formatDateTime(spot.created_at)}
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">最近追加されたスポットはありません。</li>
                  )}
                </ul>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-comments me-2" aria-hidden="true"></i>
                    最新レビュー
                  </h2>
                  <Link href="/manage/reviews" className="panel-link">
                    一覧を見る
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.recent_reviews.length ? (
                    dashboard.recent_reviews.map((review) => (
                      <li key={review.id}>
                        <span className="panel-title">
                          {review.spot_title ?? '不明'} / {review.user_username ?? review.user.username}
                        </span>
                        <span className="panel-meta">
                          {formatDateTime(review.created_at)} /{' '}
                          <span className="admin-badge admin-badge--rating">
                            <i className="fas fa-star" aria-hidden="true"></i>
                            {review.rating}
                          </span>
                        </span>
                        <p className="panel-text">{review.comment}</p>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">最近投稿されたレビューはありません。</li>
                  )}
                </ul>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-fire me-2" aria-hidden="true"></i>
                    注目スポット
                  </h2>
                  <Link href="/manage/spots?ai=1" className="panel-link">
                    AI生成を確認
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.top_spots.length ? (
                    dashboard.top_spots.map((spot) => (
                      <li key={spot.id}>
                        <span className="panel-title">{spot.title}</span>
                        <span className="panel-meta">
                          閲覧 {spot.weekly_views} / 評価{' '}
                          {spot.review_avg != null ? spot.review_avg.toFixed(1) : '-'}
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">ランキング対象のスポットがありません。</li>
                  )}
                </ul>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-robot me-2" aria-hidden="true"></i>
                    AI生成スポット
                  </h2>
                  <Link href="/manage/spots?ai=1" className="panel-link">
                    すべて見る
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.ai_generated_spots.length ? (
                    dashboard.ai_generated_spots.map((spot) => (
                      <li key={spot.id}>
                        <span className="panel-title">{spot.title}</span>
                        <span className="panel-meta">
                          <span className="admin-badge admin-badge--ai">
                            <i className="fas fa-robot" aria-hidden="true"></i>
                            AI生成
                          </span>{' '}
                          {spot.created_by ?? '不明'} / {formatDateTime(spot.updated_at)}
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">AI生成のスポットはまだありません。</li>
                  )}
                </ul>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-tags me-2" aria-hidden="true"></i>
                    人気タグ
                  </h2>
                  <Link href="/manage/tags" className="panel-link">
                    タグ管理へ
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.popular_tags.length ? (
                    dashboard.popular_tags.map((tag) => (
                      <li key={tag.id}>
                        <span className="panel-title">
                          <span className="admin-chip">#{tag.name}</span>
                        </span>
                        <span className="panel-meta">関連スポット {tag.spot_count}</span>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">タグがまだありません。</li>
                  )}
                </ul>
              </div>

              <div className="panel">
                <div className="panel-header">
                  <h2>
                    <i className="fas fa-user-friends me-2" aria-hidden="true"></i>
                    アクティブユーザー
                  </h2>
                  <Link href="/manage/users" className="panel-link">
                    ユーザー管理へ
                  </Link>
                </div>
                <ul className="panel-list">
                  {dashboard.top_reviewers.length ? (
                    dashboard.top_reviewers.map((user) => (
                      <li key={user.id}>
                        <span className="panel-title">{user.username}</span>
                        <span className="panel-meta">
                          <span className="admin-badge admin-badge--rating">
                            <i className="fas fa-comment-dots" aria-hidden="true"></i>
                            {user.review_count}
                          </span>
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="panel-empty">レビュー実績のあるユーザーがまだいません。</li>
                  )}
                </ul>
              </div>
            </section>
          </>
        ) : null}
      </div>
    </>
  );
}
