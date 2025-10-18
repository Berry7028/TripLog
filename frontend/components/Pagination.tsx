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

  const items: Array<{ label: string; page: number; disabled?: boolean; active?: boolean }> = [
    { label: '最初', page: 1, disabled: !pagination.has_previous },
    { label: '前へ', page: Math.max(1, pagination.page - 1), disabled: !pagination.has_previous },
    { label: `${pagination.page} / ${pagination.pages}`, page: pagination.page, disabled: true, active: true },
    { label: '次へ', page: Math.min(pagination.pages, pagination.page + 1), disabled: !pagination.has_next },
    { label: '最後', page: pagination.pages, disabled: !pagination.has_next },
  ];

  return (
    <nav className="mt-8 flex justify-center" aria-label="ページネーション">
      <ul className="flex flex-wrap items-center gap-2">
        {items.map((item) => (
          <li key={item.label}>
            {item.disabled ? (
              <span 
                className={`inline-block px-3 py-2 rounded-pill text-sm ${
                  item.active 
                    ? 'text-white' 
                    : 'text-gray-400 border border-gray-300'
                }`}
                style={item.active ? { 
                  backgroundColor: 'var(--brand-teal)', 
                  borderColor: 'var(--brand-teal)' 
                } : {}}
              >
                {item.label}
              </span>
            ) : (
              <Link
                href={createHref(item.page)}
                className="inline-block px-3 py-2 rounded-pill text-sm border border-gray-300 transition hover:bg-gray-100"
                style={{ color: 'var(--brand-teal-dark)' }}
              >
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
