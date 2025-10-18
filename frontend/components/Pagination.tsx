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
    { label: `${pagination.page} / ${pagination.pages}`, page: pagination.page, active: true, disabled: true },
    { label: '次へ', page: Math.min(pagination.pages, pagination.page + 1), disabled: !pagination.has_next },
    { label: '最後', page: pagination.pages, disabled: !pagination.has_next },
  ];

  return (
    <nav aria-label="ページネーション" className="mt-4">
      <ul className="pagination justify-content-center">
        {items.map((item) => (
          <li
            key={item.label}
            className={`page-item${item.disabled ? ' disabled' : ''}${item.active ? ' active' : ''}`}
          >
            {item.disabled ? (
              <span className="page-link">{item.label}</span>
            ) : (
              <Link className="page-link" href={createHref(item.page)}>
                {item.label}
              </Link>
            )}
          </li>
        ))}
      </ul>
    </nav>
  );
}
