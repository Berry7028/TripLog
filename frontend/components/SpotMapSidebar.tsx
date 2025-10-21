'use client';

import Link from 'next/link';

import type { SpotFilter, SpotSummary } from '@/types/api';

interface SpotMapSidebarProps {
  selectedSpot: SpotSummary | null;
  filter: SpotFilter;
  onFilterChange: (filter: SpotFilter) => void;
  isAuthenticated: boolean;
  recentSpots: SpotSummary[];
  onSelectRecentSpot: (spot: SpotSummary) => void;
  isLoading?: boolean;
  error?: string | null;
}

function formatDate(dateString: string | null | undefined): string {
  if (!dateString) {
    return '日付情報なし';
  }
  try {
    return new Date(dateString).toLocaleDateString('ja-JP');
  } catch {
    return dateString;
  }
}

export default function SpotMapSidebar({
  selectedSpot,
  filter,
  onFilterChange,
  isAuthenticated,
  recentSpots,
  onSelectRecentSpot,
  isLoading = false,
  error = null,
}: SpotMapSidebarProps) {
  return (
    <>
      <div className="details-surface" id="spotInfoPanel">
        <div className="d-flex justify-content-between align-items-center">
          <h3 className="details-title mb-0">スポット詳細</h3>
          {isLoading ? <small className="text-muted">更新中...</small> : null}
        </div>
        <div id="spotInfoContent" className="pt-2">
          {error ? (
            <div className="alert alert-warning mb-0" role="alert">
              データの読み込みに失敗しました。時間をおいて再度お試しください。
            </div>
          ) : selectedSpot ? (
            <>
              {selectedSpot.image ? (
                <div className="text-center mb-3">
                  <img
                    src={selectedSpot.image}
                    alt={selectedSpot.title}
                    className="img-fluid rounded mb-3"
                    style={{ maxHeight: '200px', objectFit: 'cover', width: '100%' }}
                  />
                </div>
              ) : (
                <div className="text-center text-muted py-4">
                  <i className="fas fa-image fa-3x mb-2"></i>
                  <div>画像は登録されていません。</div>
                </div>
              )}
              <h5>{selectedSpot.title}</h5>
              <p className="mb-2">{selectedSpot.description || '説明は登録されていません。'}</p>
              {selectedSpot.address ? (
                <p>
                  <i className="fas fa-map-marker-alt me-1"></i>
                  {selectedSpot.address}
                </p>
              ) : null}
              <div className="d-flex justify-content-between align-items-center">
                <small className="text-muted">
                  <i className="fas fa-user me-1"></i>
                  {selectedSpot.created_by}
                  <br />
                  <i className="fas fa-calendar me-1"></i>
                  {formatDate(selectedSpot.created_at)}
                </small>
                <Link href={`/spots/${selectedSpot.id}`} className="btn btn-primary btn-sm">
                  詳細を見る
                </Link>
              </div>
            </>
          ) : (
            <div className="text-muted py-4">地図上のスポットをクリックして詳細を表示</div>
          )}
        </div>
      </div>

      <div className="card mt-3">
        <div className="card-header">
          <h5 className="mb-0">
            <i className="fas fa-filter me-2"></i>表示フィルター
          </h5>
        </div>
        <div className="card-body">
          <label htmlFor="spot-filter" className="form-label">
            表示する投稿
          </label>
          <select
            id="spot-filter"
            className="form-select"
            value={filter}
            onChange={(event) => onFilterChange(event.target.value as SpotFilter)}
          >
            <option value="all">すべて</option>
            <option value="mine">自分のみ</option>
            <option value="others">他人のみ</option>
          </select>
          <div className="form-text">
            {isAuthenticated ? '投稿種別で地図上の表示を切り替えられます。' : 'ログイン中のみ「自分／他人」切替が有効です。'}
          </div>
        </div>
      </div>

      {recentSpots.length ? (
        <div className="card mt-3">
          <div className="card-header">
            <h5 className="mb-0">
              <i className="fas fa-list me-2"></i>最近のスポット
            </h5>
          </div>
          <div className="card-body">
            <div className="list-group">
              {recentSpots.map((spot) => (
                <Link
                  key={spot.id}
                  href={`/spots/${spot.id}`}
                  className="list-group-item list-group-item-action"
                  onMouseEnter={() => onSelectRecentSpot(spot)}
                  onFocus={() => onSelectRecentSpot(spot)}
                >
                  {spot.title}
                </Link>
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
