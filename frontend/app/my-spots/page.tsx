import Link from 'next/link';

import Pagination from '@/components/Pagination';
import SpotGrid from '@/components/SpotGrid';
import { fetchAuthStatus, fetchMySpots } from '@/lib/server-api';
import type { PaginationMeta } from '@/types/api';

const PAGE_SIZE = 12;

interface PageProps {
  searchParams: Record<string, string | string[] | undefined>;
}

function parsePage(value: string | string[] | undefined): number {
  const raw = Array.isArray(value) ? value[0] : value;
  const parsed = Number(raw);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return 1;
  }
  return Math.floor(parsed);
}

function formatJoinedAt(dateString?: string | null): string {
  if (!dateString) {
    return '-';
  }
  const date = new Date(dateString);
  if (Number.isNaN(date.getTime())) {
    return '-';
  }
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  return `${year}年${month.toString().padStart(2, '0')}月`;
}

export default async function MySpotsPage({ searchParams }: PageProps) {
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

  const mySpots = await fetchMySpots();
  const spots = mySpots.spots ?? [];
  const totalCount = spots.length;
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));
  const requestedPage = parsePage(searchParams.page);
  const page = Math.min(requestedPage, totalPages);
  const start = (page - 1) * PAGE_SIZE;
  const paginated = spots.slice(start, start + PAGE_SIZE);

  const pagination: PaginationMeta = {
    page,
    pages: totalPages,
    has_next: page < totalPages,
    has_previous: page > 1,
    total_count: totalCount,
  };

  const params = new URLSearchParams();
  Object.entries(searchParams).forEach(([key, value]) => {
    if (key === 'page') {
      return;
    }
    if (Array.isArray(value)) {
      if (value[0] !== undefined) {
        params.set(key, value[0]);
      }
    } else if (value !== undefined) {
      params.set(key, value);
    }
  });

  const stats = auth.stats ?? {
    spot_count: totalCount,
    review_count: 0,
    favorite_count: auth.user?.profile?.favorite_spots?.length ?? 0,
  };

  return (
    <>
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

          {paginated.length > 0 ? (
            <>
              <SpotGrid spots={paginated} />
              <Pagination pagination={pagination} basePath="/my-spots" searchParams={params} />
            </>
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
      </div>

      <div className="row mt-5">
        <div className="col-md-4 mb-3">
          <div className="card text-center h-100">
            <div className="card-body">
              <i className="fas fa-map-marked-alt fa-2x text-primary mb-2"></i>
              <h4>{stats.spot_count}</h4>
              <p className="text-muted mb-0">投稿したスポット</p>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card text-center h-100">
            <div className="card-body">
              <i className="fas fa-star fa-2x text-warning mb-2"></i>
              <h4>{stats.review_count}</h4>
              <p className="text-muted mb-0">投稿したレビュー</p>
            </div>
          </div>
        </div>
        <div className="col-md-4 mb-3">
          <div className="card text-center h-100">
            <div className="card-body">
              <i className="fas fa-calendar fa-2x text-success mb-2"></i>
              <h4>{formatJoinedAt(auth.user?.date_joined)}</h4>
              <p className="text-muted mb-0">登録日</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
