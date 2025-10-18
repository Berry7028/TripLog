'use client';

import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { FormEvent, useEffect, useState } from 'react';

interface SearchSortBarProps {
  searchQuery: string;
  sortMode: 'recent' | 'relevance';
  totalCount: number;
  recommendationNotice?: string | null;
}

export default function SearchSortBar({ searchQuery, sortMode, totalCount, recommendationNotice }: SearchSortBarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [keyword, setKeyword] = useState(searchQuery);

  useEffect(() => {
    setKeyword(searchQuery);
  }, [searchQuery]);

  const updateQuery = (next: Record<string, string | undefined>) => {
    const params = new URLSearchParams(searchParams.toString());
    Object.entries(next).forEach(([key, value]) => {
      if (value) {
        params.set(key, value);
      } else {
        params.delete(key);
      }
    });
    params.delete('page');
    router.push(`${pathname}?${params.toString()}`);
    router.refresh();
  };

  const handleSortChange = (value: 'recent' | 'relevance') => {
    updateQuery({ sort: value });
  };

  return (
    <div className="space-y-3">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
        <div className="flex items-center gap-3">
          <label htmlFor="sortMode" className="font-bold text-base whitespace-nowrap" style={{ color: '#333' }}>
            並び順
          </label>
          <select
            id="sortMode"
            value={sortMode}
            onChange={(event) => handleSortChange(event.target.value as 'recent' | 'relevance')}
            className="form-select border border-gray-400 px-4 py-1.5 text-base transition-colors focus:border-[#6B9080] focus:outline-none"
            style={{ borderRadius: '8px', minWidth: '120px', backgroundColor: '#fff' }}
          >
            <option value="recent">新着順</option>
            <option value="relevance">おすすめ順(β)</option>
          </select>
        </div>

        {recommendationNotice && (
          <div className="alert alert-info mb-0 py-2 px-3 text-sm rounded-lg bg-blue-100 text-blue-800">
            <i className="fas fa-info-circle me-1"></i>
            {recommendationNotice}
          </div>
        )}
      </div>

      {searchQuery && (
        <div className="alert alert-info rounded-lg bg-blue-100 text-blue-800 p-3">
          <i className="fas fa-search me-2"></i>
          「{searchQuery}」の検索結果: {totalCount}件
        </div>
      )}
    </div>
  );
}
