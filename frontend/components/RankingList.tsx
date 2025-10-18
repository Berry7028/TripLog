import Image from 'next/image';
import Link from 'next/link';

import type { SpotSummary } from '@/types/api';

interface RankingListProps {
  spots: SpotSummary[];
}

function formatWeeklyViews(count?: number): string {
  if (typeof count !== 'number') {
    return '0 回';
  }
  return `${count.toLocaleString('ja-JP')} 回`;
}

export default function RankingList({ spots }: RankingListProps) {
  if (spots.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
        ランキングデータがまだありません。
      </div>
    );
  }

  return (
    <ol className="space-y-4">
      {spots.map((spot, index) => (
        <li key={spot.id}>
          <article className="flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm transition hover:-translate-y-1 hover:shadow-lg sm:flex-row sm:items-stretch">
            <div className="flex items-center justify-center rounded-xl bg-primary/10 px-6 py-4 text-3xl font-bold text-primary sm:text-4xl">
              {index + 1}
            </div>
            <div className="flex flex-1 flex-col gap-4 sm:flex-row">
              <div className="relative h-32 w-full overflow-hidden rounded-xl bg-slate-100 sm:h-32 sm:w-44">
                {spot.image ? (
                  <Image
                    src={spot.image}
                    alt={spot.title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 640px) 100vw, 176px"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-sm text-slate-400">No Image</div>
                )}
              </div>
              <div className="flex flex-1 flex-col justify-between gap-3">
                <header className="space-y-1">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h2 className="text-lg font-semibold text-slate-900">
                      <Link href={`/spots/${spot.id}`} className="hover:text-primary">
                        {spot.title}
                      </Link>
                    </h2>
                    <span className="flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                      <span className="inline-flex h-2 w-2 rounded-full bg-primary" aria-hidden />
                      週間閲覧数: {formatWeeklyViews(spot.weekly_views)}
                    </span>
                  </div>
                  {spot.address ? (
                    <p className="truncate text-sm text-slate-500" title={spot.address}>
                      {spot.address}
                    </p>
                  ) : null}
                </header>
                <div className="flex flex-wrap gap-2 text-xs text-slate-500">
                  {spot.tags.length > 0
                    ? spot.tags.map((tag) => (
                        <span key={tag} className="rounded-full bg-slate-100 px-2 py-1">
                          #{tag}
                        </span>
                      ))
                    : (
                        <span className="rounded-full bg-slate-100 px-2 py-1 text-slate-400">タグ未設定</span>
                      )}
                </div>
              </div>
            </div>
          </article>
        </li>
      ))}
    </ol>
  );
}
