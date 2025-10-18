import Link from 'next/link';
import { Fragment } from 'react';

import type { PaginationMeta } from '@/types/api';

interface PaginationProps {
  pagination: PaginationMeta;
  basePath?: string;
  searchParams: URLSearchParams;
}

export default function Pagination({ pagination, basePath = '/', searchParams }: PaginationProps) {
  if (pagination.pages <= 1) {
    return null;
  }

  const createHref = (page: number) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('page', String(page));
    const query = params.toString();
    return query ? `${basePath}?${query}` : basePath;
  };

  const items: Array<{ label: string; page: number; disabled?: boolean }> = [
    { label: '最初', page: 1, disabled: !pagination.has_previous },
    { label: '前へ', page: Math.max(1, pagination.page - 1), disabled: !pagination.has_previous },
    { label: `${pagination.page} / ${pagination.pages}`, page: pagination.page, disabled: true },
    { label: '次へ', page: Math.min(pagination.pages, pagination.page + 1), disabled: !pagination.has_next },
    { label: '最後', page: pagination.pages, disabled: !pagination.has_next },
  ];

  return (
    <nav className="mt-8 flex justify-center">
      <ul className="flex flex-wrap items-center gap-2 text-sm">
        {items.map((item) => (
          <Fragment key={item.label}>
            {item.disabled ? (
              <span className="rounded-full border border-slate-200 px-3 py-1 text-slate-400">
                {item.label}
              </span>
            ) : (
              <Link
                href={createHref(item.page)}
                className="rounded-full border border-slate-300 px-3 py-1 text-slate-700 transition hover:bg-slate-100"
              >
                {item.label}
              </Link>
            )}
          </Fragment>
        ))}
      </ul>
    </nav>
  );
}
