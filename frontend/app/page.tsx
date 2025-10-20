import SearchSortBar from '@/components/SearchSortBar';
import SpotGrid from '@/components/SpotGrid';
import Pagination from '@/components/Pagination';
import { fetchHomeSpots } from '@/lib/server-api';
import type { HomeResponse } from '@/types/api';

interface PageProps {
  searchParams: Record<string, string | string[] | undefined>;
}

const FALLBACK_PAGINATION: HomeResponse['pagination'] = {
  page: 1,
  pages: 1,
  has_next: false,
  has_previous: false,
  total_count: 0,
};

function resolveParam(value: string | string[] | undefined): string | undefined {
  if (Array.isArray(value)) {
    return value[0];
  }
  return value;
}

export default async function HomePage({ searchParams }: PageProps) {
  let data: HomeResponse;
  let loadError: string | null = null;

  try {
    data = await fetchHomeSpots(searchParams);
  } catch (error) {
    console.error('Failed to load home data', error);
    const searchValue = resolveParam(searchParams.search);
    const sortValue = resolveParam(searchParams.sort);

    data = {
      spots: [],
      pagination: { ...FALLBACK_PAGINATION },
      search_query: searchValue ?? '',
      sort_mode: sortValue === 'relevance' ? 'relevance' : 'recent',
      recommendation_notice: null,
    };
    loadError = 'スポットの読み込みに失敗しました。時間をおいて再度お試しください。';
  }
  const params = new URLSearchParams();
  Object.entries(searchParams).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => params.append(key, item));
    } else if (value !== undefined) {
      params.set(key, value);
    }
  });

  return (
    <div className="space-y-6">
      <h2 className="section-title">いちらん</h2>
      {loadError ? (
        <div className="alert alert-warning" role="alert">
          {loadError}
        </div>
      ) : null}
      <SearchSortBar
        searchQuery={data.search_query}
        sortMode={data.sort_mode}
        totalCount={data.pagination.total_count}
        recommendationNotice={data.recommendation_notice}
      />
      <SpotGrid spots={data.spots} sortMode={data.sort_mode} />
      <Pagination pagination={data.pagination} searchParams={params} />
    </div>
  );
}
