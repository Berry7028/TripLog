import Image from 'next/image';
import Link from 'next/link';

import FavoriteButton from '@/components/FavoriteButton';
import ReviewForm from '@/components/ReviewForm';
import ReviewList from '@/components/ReviewList';
import ShareButton from '@/components/ShareButton';
import ViewTracker from '@/components/ViewTracker';
import { fetchSpotDetail } from '@/lib/server-api';

interface SpotDetailPageProps {
  params: { id: string };
}

export default async function SpotDetailPage({ params }: SpotDetailPageProps) {
  const spotId = Number(params.id);
  const data = await fetchSpotDetail(spotId);
  const { spot, viewer } = data;

  return (
    <>
      <ViewTracker spotId={spotId} enabled={viewer.is_authenticated} />
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            {spot.image && (
              <img
                src={spot.image}
                className="card-img-top spot-hero"
                alt={spot.title}
                style={{ height: '400px', objectFit: 'cover' }}
              />
            )}

            <div className="card-body">
              <h1 className="card-title">{spot.title}</h1>
              <div className="mb-3">
                <div className="d-flex flex-wrap gap-2">
                  {viewer.is_authenticated ? (
                    <FavoriteButton
                      spotId={spotId}
                      initialFavorite={data.is_favorite}
                      disabled={!viewer.is_authenticated}
                    />
                  ) : (
                    <Link href="/login" className="btn btn-outline-danger btn-sm">
                      <i className="fas fa-heart me-1"></i>お気に入りに追加（ログイン）
                    </Link>
                  )}
                  <ShareButton url={data.share_url} />
                </div>
              </div>

              <div className="mb-3">
                <small className="text-muted">
                  <i className="fas fa-user me-1"></i>投稿者: {spot.created_by_detail?.username ?? '不明'}
                  <span className="ms-3">
                    <i className="fas fa-calendar me-1"></i>
                    {spot.created_at ? new Date(spot.created_at).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }) : '不明'}
                  </span>
                </small>
              </div>

              {spot.address && (
                <p className="mb-3">
                  <i className="fas fa-map-marker-alt me-2"></i>
                  {spot.address}
                </p>
              )}

              <p className="card-text" style={{ whiteSpace: 'pre-wrap' }}>
                {spot.description}
              </p>

              <div className="mb-3">
                <small className="text-muted">
                  緯度: {spot.latitude.toFixed(4)}, 経度: {spot.longitude.toFixed(4)}
                </small>
              </div>

              {spot.tags.length > 0 && (
                <div className="mb-2">
                  {spot.tags.map((tag: string) => (
                    <span key={tag} className="badge bg-secondary me-1">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* レビューセクション */}
          <div className="card mt-4">
            <div className="card-header">
              <h3>
                <i className="fas fa-star me-2"></i>レビュー
              </h3>
              {data.avg_rating && (
                <div className="rating">
                  平均評価:{' '}
                  {Array.from({ length: 5 }).map((_, i) => (
                    <i key={i} className={i < Math.round(data.avg_rating!) ? 'fas fa-star' : 'far fa-star'}></i>
                  ))}
                  ({data.reviews.length}件)
                </div>
              )}
            </div>
            <div className="card-body">
              <ReviewForm spotId={spotId} canReview={viewer.is_authenticated && viewer.can_review} />
              <ReviewList reviews={data.reviews} avgRating={data.avg_rating} />
            </div>
          </div>
        </div>

        <div className="col-md-4">
          {/* 地図表示エリア */}
          <div className="card">
            <div className="card-header">
              <h5>
                <i className="fas fa-map me-2"></i>位置情報
              </h5>
            </div>
            <div className="card-body p-0">
              <iframe
                title="map"
                src={`https://www.openstreetmap.org/export/embed.html?bbox=${spot.longitude - 0.01}%2C${spot.latitude - 0.01}%2C${spot.longitude + 0.01}%2C${spot.latitude + 0.01}&layer=mapnik&marker=${spot.latitude}%2C${spot.longitude}`}
                style={{ height: '300px', width: '100%', border: 'none' }}
                loading="lazy"
              />
            </div>
            <div className="card-footer">
              <small className="text-muted">
                緯度: {spot.latitude.toFixed(4)}, 経度: {spot.longitude.toFixed(4)}
              </small>
            </div>
          </div>

          {/* 関連スポット */}
          {data.related_spots.length > 0 && (
            <div className="card mt-4">
              <div className="card-header">
                <h5>
                  <i className="fas fa-user me-2"></i>
                  {spot.created_by_detail?.username ?? '投稿者'}さんの他の投稿
                </h5>
              </div>
              <div className="card-body">
                {data.related_spots.map((related: any) => (
                  <div key={related.id} className="mb-2">
                    <Link href={`/spots/${related.id}`} className="text-decoration-none">
                      {related.title}
                    </Link>
                    <br />
                    <small className="text-muted">
                      {related.created_at ? new Date(related.created_at).toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' }) : ''}
                    </small>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="mt-4">
        <Link href="/" className="btn btn-secondary">
          <i className="fas fa-arrow-left me-2"></i>一覧に戻る
        </Link>
      </div>
    </>
  );
}
