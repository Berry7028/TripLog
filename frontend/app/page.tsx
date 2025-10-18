import Link from 'next/link';

import SearchSortBar from '@/components/SearchSortBar';
import SpotGrid from '@/components/SpotGrid';
import Pagination from '@/components/Pagination';
import { fetchHomeSpots } from '@/lib/server-api';

interface PageProps {
  searchParams: Record<string, string | string[] | undefined>;
}

export default async function HomePage({ searchParams }: PageProps) {
  const data = await fetchHomeSpots(searchParams);
  const params = new URLSearchParams();
  Object.entries(searchParams).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => params.append(key, item));
    } else if (value !== undefined) {
      params.set(key, value);
    }
  });

  const hasSpots = data.spots.length > 0;

  return (
    <div className="row">
      <div className="col-12">
        <h2 className="section-title">いちらん</h2>
        <SearchSortBar
          searchQuery={data.search_query}
          sortMode={data.sort_mode}
          totalCount={data.pagination.total_count}
          recommendationNotice={data.recommendation_notice}
        />

        {hasSpots ? (
          <>
            <SpotGrid spots={data.spots} sortMode={data.sort_mode} />
            <Pagination pagination={data.pagination} searchParams={params} />
          </>
        ) : (
          <div className="text-center py-5">
            <i className="fas fa-map-marked-alt fa-5x text-muted mb-3"></i>
            <h3>まだスポットが投稿されていません</h3>
            <p className="text-muted">最初のスポットを投稿してみませんか？</p>
            {data.viewer_is_authenticated ? (
              <Link href="/spots/add" className="btn btn-primary">
                <i className="fas fa-plus me-2"></i>スポットを投稿する
              </Link>
            ) : (
              <Link href="/register" className="btn btn-primary">
                <i className="fas fa-user-plus me-2"></i>新規登録してスポットを投稿
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
