import Link from 'next/link';

import LogoutButton from './LogoutButton';

interface HeaderProps {
  currentUser: {
    id: number;
    username: string;
  } | null;
}

const navItems = [
  { href: '/', label: 'ホーム' },
  { href: '/ranking', label: 'ランキング' },
  { href: '/map', label: 'マップ' },
  { href: '/plan', label: 'プラン' },
];

export default function Header({ currentUser }: HeaderProps) {
  return (
    <header className="border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="text-xl font-semibold text-slate-900">
          旅ログマップ
        </Link>
        <nav className="hidden items-center gap-4 text-sm font-medium text-slate-700 md:flex">
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-full px-3 py-2 transition hover:bg-slate-100"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="flex items-center gap-3 text-sm">
          {currentUser ? (
            <>
              <span className="hidden text-slate-600 sm:inline">{currentUser.username} さん</span>
              <Link
                href="/my-spots"
                className="rounded-full border border-primary px-3 py-1 text-primary transition hover:bg-primary hover:text-white"
              >
                マイスポット
              </Link>
              <Link
                href="/spots/add"
                className="hidden rounded-full bg-primary px-3 py-1 text-white transition hover:bg-blue-600 sm:inline"
              >
                投稿する
              </Link>
              <LogoutButton />
            </>
          ) : (
            <>
              <Link href="/spots/add" className="rounded-full bg-primary px-3 py-1 text-white transition hover:bg-blue-600">
                投稿する
              </Link>
              <Link href="/login" className="rounded-full border border-slate-200 px-3 py-1 text-slate-700 transition hover:bg-slate-100">
                ログイン
              </Link>
              <Link href="/register" className="rounded-full border border-slate-200 px-3 py-1 text-slate-700 transition hover:bg-slate-100">
                新規登録
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
