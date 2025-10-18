'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';

interface SearchSortBarProps {
  searchQuery: string;
  sortMode: 'recent' | 'relevance';
  totalCount: number;
  recommendationNotice?: string | null;
}

export default function SearchSortBar({
  searchQuery,
  sortMode,
  totalCount,
  recommendationNotice,
}: SearchSortBarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const handleSortChange = (value: 'recent' | 'relevance') => {
    const params = new URLSearchParams(searchParams?.toString());
    if (searchQuery) {
      params.set('search', searchQuery);
    } else {
      params.delete('search');
    }
    params.set('sort', value);
    params.delete('page');
    const query = params.toString();
    router.push(query ? `${pathname}?${query}` : pathname);
    router.refresh();
  };

  return (
    <div className="mb-4">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-3 gap-2">
        <form className="d-flex align-items-center gap-3 mb-0" onSubmit={(event) => event.preventDefault()}>
          <label htmlFor="sortMode" className="form-label mb-0 fw-bold" style={{ color: '#333', whiteSpace: 'nowrap' }}>
            並び順
          </label>
          <select
            id="sortMode"
            value={sortMode}
            onChange={(event) => handleSortChange(event.target.value as 'recent' | 'relevance')}
            className="form-select"
            style={{ minWidth: '120px' }}
          >
            <option value="recent">新着順</option>
            <option value="relevance">おすすめ順(β)</option>
          </select>
        </form>

        {recommendationNotice ? (
          <div className="alert alert-info mb-0 py-2 px-3 small d-flex align-items-center" role="status">
            <i className="fas fa-info-circle me-1"></i>
            <span>{recommendationNotice}</span>
          </div>
        ) : null}
      </div>

      {searchQuery ? (
        <div className="alert alert-info" role="status">
          <i className="fas fa-search me-2"></i>
          「{searchQuery}」の検索結果: {totalCount}件
        </div>
      ) : null}
    </div>
  );
}
