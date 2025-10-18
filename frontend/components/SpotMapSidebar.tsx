'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useMemo } from 'react';

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
  } catch (error) {
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
  const detailContent = useMemo(() => {
    if (!selectedSpot) {
      return <p className="text-sm text-slate-500">地図上のスポットをクリックして詳細を表示します。</p>;
    }
    return (
      <div className="space-y-4 text-sm text-slate-600">
        <div className="space-y-3">
          {selectedSpot.image ? (
            <div className="relative h-48 w-full overflow-hidden rounded-xl bg-slate-100">
              <Image
                src={selectedSpot.image}
                alt={selectedSpot.title}
                fill
                sizes="(max-width: 768px) 100vw, 320px"
                className="object-cover"
              />
            </div>
          ) : (
            <div className="flex h-48 w-full items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 text-slate-400">
              画像は登録されていません
            </div>
          )}
          <div className="space-y-1">
            <h3 className="text-lg font-semibold text-slate-900">{selectedSpot.title}</h3>
            <p className="text-xs text-slate-500">{selectedSpot.address || '住所情報なし'}</p>
          </div>
        </div>
        <p className="whitespace-pre-wrap text-sm leading-relaxed">{selectedSpot.description || '説明は登録されていません。'}</p>
        <div className="rounded-lg bg-slate-100 px-4 py-3 text-xs text-slate-600">
          <p>
            投稿者: <span className="font-medium text-slate-800">{selectedSpot.created_by}</span>
          </p>
          <p>投稿日: {formatDate(selectedSpot.created_at)}</p>
          {selectedSpot.tags?.length ? (
            <p className="mt-2 flex flex-wrap gap-2 text-[11px]">
              {selectedSpot.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-white px-2 py-1 text-slate-500 shadow-sm">
                  #{tag}
                </span>
              ))}
            </p>
          ) : null}
        </div>
        <div>
          <Link
            href={`/spots/${selectedSpot.id}`}
            className="inline-flex items-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-600"
          >
            詳細ページへ
          </Link>
        </div>
      </div>
    );
  }, [selectedSpot]);

  return (
    <div className="space-y-6">
      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">スポット詳細</h2>
          {isLoading && <span className="text-xs text-slate-400">更新中...</span>}
        </div>
        {error ? (
          <p className="text-sm text-red-500">データの読み込みに失敗しました。時間をおいて再度お試しください。</p>
        ) : (
          detailContent
        )}
      </section>

      <section className="space-y-3 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">表示フィルター</h2>
          {!isAuthenticated && (
            <span className="text-[11px] text-slate-400">ログインで詳細な切替が可能</span>
          )}
        </div>
        <div className="space-y-2 text-sm text-slate-600">
          <label className="block text-xs font-medium text-slate-500" htmlFor="spot-filter">
            表示する投稿
          </label>
          <select
            id="spot-filter"
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30"
            value={filter}
            onChange={(event) => onFilterChange(event.target.value as SpotFilter)}
          >
            <option value="all">すべて</option>
            <option value="mine">自分のみ</option>
            <option value="others">他人のみ</option>
          </select>
          <p className="text-xs text-slate-400">{isAuthenticated ? '投稿種別で地図上の表示を切り替えられます。' : 'ログイン中のみ「自分／他人」切替が有効です。'}</p>
        </div>
      </section>

      <section className="space-y-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-900">最近のスポット</h2>
          <span className="text-xs text-slate-400">{recentSpots.length} 件</span>
        </div>
        {recentSpots.length === 0 ? (
          <p className="text-sm text-slate-500">最近のスポット情報がまだありません。</p>
        ) : (
          <div className="space-y-3">
            {recentSpots.map((spot) => (
              <button
                type="button"
                key={spot.id}
                onClick={() => onSelectRecentSpot(spot)}
                className="flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 text-left transition hover:border-primary/60 hover:shadow"
              >
                <div className="relative h-16 w-16 overflow-hidden rounded-lg bg-slate-100">
                  {spot.image ? (
                    <Image src={spot.image} alt={spot.title} fill sizes="64px" className="object-cover" />
                  ) : (
                    <span className="flex h-full w-full items-center justify-center text-[11px] text-slate-400">No Image</span>
                  )}
                </div>
                <div className="flex-1 space-y-1 text-xs text-slate-500">
                  <p className="text-sm font-semibold text-slate-900">{spot.title}</p>
                  <p className="line-clamp-2">{spot.description || '説明は登録されていません。'}</p>
                  <p>投稿日: {formatDate(spot.created_at)}</p>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
