import Link from 'next/link';

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
    <nav className="mt-4" aria-label="ページネーション">
      <ul className="pagination justify-content-center flex-wrap gap-2">
        {items.map((item) => (
          <li
            key={item.label}
            className={`page-item${item.disabled ? ' disabled' : ''}${item.active ? ' active' : ''}`}
            aria-current={item.active ? 'page' : undefined}
          >
            {item.disabled ? (
              <span className="page-link">{item.label}</span>
            ) : (
              <Link href={createHref(item.page)} className="page-link">
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
