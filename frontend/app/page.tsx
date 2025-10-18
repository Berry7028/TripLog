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

  return (
    <div className="space-y-6">
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
