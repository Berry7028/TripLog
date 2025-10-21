'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navItems: Array<{
  href: string;
  label: string;
  icon: string;
  isActive: (pathname: string) => boolean;
}> = [
  {
    href: '/manage',
    label: 'ダッシュボード',
    icon: 'fas fa-chart-line',
    isActive: (pathname) => pathname === '/manage',
  },
  {
    href: '/manage/spots',
    label: 'スポット管理',
    icon: 'fas fa-map-marker-alt',
    isActive: (pathname) => pathname.startsWith('/manage/spots'),
  },
  {
    href: '/manage/reviews',
    label: 'レビュー管理',
    icon: 'fas fa-comments',
    isActive: (pathname) => pathname.startsWith('/manage/reviews'),
  },
  {
    href: '/manage/tags',
    label: 'タグ管理',
    icon: 'fas fa-tags',
    isActive: (pathname) => pathname.startsWith('/manage/tags'),
  },
  {
    href: '/manage/users',
    label: 'ユーザー管理',
    icon: 'fas fa-users',
    isActive: (pathname) => pathname.startsWith('/manage/users'),
  },
  {
    href: '/manage/groups',
    label: 'グループ・権限',
    icon: 'fas fa-user-shield',
    isActive: (pathname) => pathname.startsWith('/manage/groups'),
  },
  {
    href: '/manage/profiles',
    label: 'プロフィール',
    icon: 'fas fa-id-card',
    isActive: (pathname) => pathname.startsWith('/manage/profiles'),
  },
  {
    href: '/manage/spot-views',
    label: '閲覧ログ',
    icon: 'fas fa-eye',
    isActive: (pathname) => pathname.startsWith('/manage/spot-views'),
  },
  {
    href: '/manage/recommendations',
    label: 'AIおすすめ',
    icon: 'fas fa-robot',
    isActive: (pathname) => pathname.startsWith('/manage/recommendations'),
  },
];

export default function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="admin-sidebar">
      <div className="admin-brand">
        <i className="fas fa-tools me-2" aria-hidden="true"></i>
        管理メニュー
      </div>
      <nav className="admin-nav" aria-label="管理メニュー">
        {navItems.map((item) => {
          const active = item.isActive(pathname);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`admin-nav-link${active ? ' is-active' : ''}`}
            >
              <i className={`${item.icon}`} aria-hidden="true"></i>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
