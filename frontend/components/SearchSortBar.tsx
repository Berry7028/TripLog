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

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    updateQuery({ search: keyword || undefined });
  };

  const handleSortChange = (value: 'recent' | 'relevance') => {
    updateQuery({ sort: value });
  };

  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-center md:justify-between">
      <form onSubmit={handleSubmit} className="flex w-full max-w-xl items-center gap-3">
        <input
          type="text"
          placeholder="スポットを検索"
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
          className="flex-1 rounded-full border border-slate-300 px-4 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button type="submit" className="rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white">
          検索
        </button>
        <div className="flex items-center gap-2 text-sm">
          <label htmlFor="sortMode" className="font-semibold text-slate-600">
            並び順
          </label>
          <select
            id="sortMode"
            value={sortMode}
            onChange={(event) => handleSortChange(event.target.value as 'recent' | 'relevance')}
            className="rounded-full border border-slate-300 px-3 py-1 text-sm"
          >
            <option value="recent">新着順</option>
            <option value="relevance">おすすめ順(β)</option>
          </select>
        </div>
      </form>
      <div className="flex flex-col gap-1 text-xs text-slate-500 md:text-right">
        <span>検索結果: {totalCount}件</span>
        {recommendationNotice ? <span className="text-amber-600">{recommendationNotice}</span> : null}
      </div>
    </div>
  );
}
