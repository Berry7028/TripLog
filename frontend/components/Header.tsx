'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';

import LogoutButton from './LogoutButton';
import { fetchAuthStatus } from '@/lib/server-api';

interface CurrentUser {
  id: number;
  username: string;
  is_staff?: boolean;
}

interface HeaderProps {
  currentUser?: CurrentUser | null;
}

const navItems = [
  { href: '/map', label: 'まっぷ' },
  { href: '/ranking', label: 'らんきんぐ' },
  { href: '/spots/add', label: 'とうこう' },
  { href: '/plan', label: 'ぷらん' },
];

function isActivePath(currentPath: string, target: string): boolean {
  if (target === '/') {
    return currentPath === '/';
  }
  return currentPath === target || currentPath.startsWith(`${target}/`);
}

export default function Header({ currentUser: initialUser }: HeaderProps) {
  const [currentUser, setCurrentUser] = useState<CurrentUser | null | undefined>(initialUser);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortMode, setSortMode] = useState<string | null>(null);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (initialUser === undefined) {
      fetchAuthStatus()
        .then((auth) => {
          if (auth.is_authenticated && auth.user) {
            setCurrentUser({
              id: auth.user.id,
              username: auth.user.username,
              is_staff: auth.user.is_staff,
            });
          } else {
            setCurrentUser(null);
          }
        })
        .catch(() => {
          setCurrentUser(null);
        });
    } else {
      setCurrentUser(initialUser ?? null);
    }
  }, [initialUser]);

  useEffect(() => {
    if (!searchParams) {
      return;
    }
    const nextSearch = searchParams.get('search') ?? '';
    const nextSort = searchParams.get('sort');
    setSearchQuery(nextSearch);
    setSortMode(nextSort);
  }, [searchParams]);

  useEffect(() => {
    setIsMenuOpen(false);
  }, [pathname]);

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const params = new URLSearchParams();
    if (searchQuery.trim()) {
      params.set('search', searchQuery.trim());
    }
    if (sortMode) {
      params.set('sort', sortMode);
    }
    const query = params.toString();
    router.push(query ? `/?${query}` : '/');
    router.refresh();
    setIsMenuOpen(false);
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    setSortMode(null);
    router.push('/');
    router.refresh();
    setIsMenuOpen(false);
  };

  return (
    <nav className="navbar navbar-expand-lg navbar-dark navbar-custom shadow-sm">
      <div className="container">
        <Link href="/" className="navbar-brand" onClick={() => setIsMenuOpen(false)}>
          <i className="fas fa-map-marked-alt me-2"></i>旅ログまっぷ
        </Link>
        <button
          className="navbar-toggler"
          type="button"
          aria-controls="navbarNav"
          aria-expanded={isMenuOpen}
          aria-label="メニューを切り替え"
          onClick={() => setIsMenuOpen((prev) => !prev)}
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className={`collapse navbar-collapse ${isMenuOpen ? 'show' : ''}`} id="navbarNav">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {navItems.map((item) => (
              <li className="nav-item" key={item.href}>
                <Link
                  href={item.href}
                  className={`nav-link ${isActivePath(pathname, item.href) ? 'active' : ''}`}
                  onClick={() => setIsMenuOpen(false)}
                >
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          <form
            onSubmit={handleSearchSubmit}
            className="d-flex me-lg-3 my-3 my-lg-0 ms-lg-auto w-100 w-lg-auto"
            role="search"
          >
            <div className="input-group search-group w-100">
              <input
                type="search"
                className="form-control search-input"
                placeholder="検索"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                aria-label="スポットを検索"
              />
              {searchQuery ? (
                <button
                  type="button"
                  className="btn btn-clear"
                  onClick={handleClearSearch}
                  aria-label="検索条件をクリア"
                >
                  ×
                </button>
              ) : null}
            </div>
          </form>

          <ul className="navbar-nav align-items-lg-center">
            {currentUser ? (
              <li className="nav-item d-flex align-items-center">
                <Link href="/my-spots" className="avatar-circle me-2" onClick={() => setIsMenuOpen(false)}>
                  <i className="fas fa-user"></i>
                </Link>
                <Link href="/profile" className="nav-link px-0 me-lg-2 text-white" onClick={() => setIsMenuOpen(false)}>
                  {currentUser.username}
                </Link>
                {currentUser.is_staff ? (
                  <a
                    href="/manage/"
                    className="nav-link px-0 me-lg-2 text-white"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <i className="fas fa-cog me-1"></i>管理
                  </a>
                ) : null}
                <LogoutButton
                  onLoggedOut={() => setIsMenuOpen(false)}
                  className="btn btn-link nav-link p-0 text-white d-flex align-items-center"
                />
              </li>
            ) : (
              <>
                <li className="nav-item">
                  <Link href="/login" className="nav-link" onClick={() => setIsMenuOpen(false)}>
                    <i className="fas fa-sign-in-alt me-1"></i>ログイン
                  </Link>
                </li>
                <li className="nav-item">
                  <Link href="/register" className="nav-link" onClick={() => setIsMenuOpen(false)}>
                    <i className="fas fa-user-plus me-1"></i>新規登録
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}
