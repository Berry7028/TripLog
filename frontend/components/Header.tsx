'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import LogoutButton from './LogoutButton';
import { fetchAuthStatus } from '@/lib/client-api';
import type { AuthStatusResponse } from '@/types/api';

interface HeaderUser {
  id: number;
  username: string;
  isStaff?: boolean;
}

interface HeaderProps {
  currentUser?: HeaderUser | null;
}

const navItems = [
  { href: '/map', label: 'まっぷ' },
  { href: '/ranking', label: 'らんきんぐ' },
  { href: '/spots/add', label: 'とうこう' },
  { href: '/plan', label: 'ぷらん' },
];

export default function Header({ currentUser: initialUser }: HeaderProps) {
  const [currentUser, setCurrentUser] = useState<HeaderUser | null | undefined>(
    initialUser,
  );
  const [isNavOpen, setIsNavOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortParam, setSortParam] = useState('');

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const params = new URLSearchParams(window.location.search);
    setSearchQuery(params.get('search') ?? '');
    setSortParam(params.get('sort') ?? '');
  }, []);

  useEffect(() => {
    if (initialUser !== undefined) {
      return;
    }
    fetchAuthStatus()
      .then((auth: AuthStatusResponse) => {
        if (auth.is_authenticated && auth.user) {
          setCurrentUser({
            id: auth.user.id,
            username: auth.user.username,
            isStaff: Boolean(auth.user.is_staff),
          });
        } else {
          setCurrentUser(null);
        }
      })
      .catch(() => {
        setCurrentUser(null);
      });
  }, [initialUser]);

  const handleSearchSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const destination = new URL('/', window.location.origin);
    const trimmed = searchQuery.trim();
    if (trimmed) {
      destination.searchParams.set('search', trimmed);
    }
    if (sortParam) {
      destination.searchParams.set('sort', sortParam);
    }
    window.location.href = destination.toString();
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    const destination = new URL('/', window.location.origin);
    if (sortParam) {
      destination.searchParams.set('sort', sortParam);
    }
    window.location.href = destination.toString();
  };

  const closeNav = () => setIsNavOpen(false);

  return (
    <nav className="navbar navbar-expand-lg navbar-dark navbar-custom shadow-sm">
      <div className="container">
        <Link href="/" className="navbar-brand" onClick={closeNav}>
          <i className="fas fa-map-marked-alt me-2" aria-hidden="true"></i>
          旅ログまっぷ
        </Link>

        <button
          type="button"
          className="navbar-toggler"
          aria-label="メニューを開く"
          aria-expanded={isNavOpen}
          onClick={() => setIsNavOpen((open) => !open)}
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        <div className={`collapse navbar-collapse${isNavOpen ? ' show' : ''}`}>
          <ul className="navbar-nav me-auto mb-2 mb-lg-0">
            {navItems.map((item) => (
              <li className="nav-item" key={item.href}>
                <Link href={item.href} className="nav-link" onClick={closeNav}>
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>

          <form className="d-flex me-lg-3 mb-3 mb-lg-0" onSubmit={handleSearchSubmit}>
            <div className="input-group search-group w-100">
              <input
                className="form-control search-input"
                type="search"
                name="search"
                placeholder="検索"
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                aria-label="スポット検索"
              />
              {sortParam ? <input type="hidden" name="sort" value={sortParam} /> : null}
              {searchQuery ? (
                <button type="button" className="btn btn-clear" onClick={handleClearSearch}>
                  ×
                </button>
              ) : null}
            </div>
          </form>

          <ul className="navbar-nav mb-2 mb-lg-0">
            {currentUser ? (
              <li className="nav-item d-flex align-items-center gap-2">
                <Link href="/my-spots" className="avatar-circle" onClick={closeNav}>
                  <span className="visually-hidden">マイスポット</span>
                  <i className="fas fa-user" aria-hidden="true"></i>
                </Link>
                <Link href="/profile" className="nav-link" onClick={closeNav}>
                  {currentUser.username}
                </Link>
                {currentUser.isStaff ? (
                  <Link href="/manage/" className="nav-link" onClick={closeNav}>
                    <i className="fas fa-cog me-1" aria-hidden="true"></i>
                    管理
                  </Link>
                ) : null}
                <LogoutButton className="nav-link d-flex align-items-center" />
              </li>
            ) : (
              <>
                <li className="nav-item">
                  <Link href="/login" className="nav-link" onClick={closeNav}>
                    <i className="fas fa-sign-in-alt me-1" aria-hidden="true"></i>
                    ログイン
                  </Link>
                </li>
                <li className="nav-item">
                  <Link href="/register" className="nav-link" onClick={closeNav}>
                    <i className="fas fa-user-plus me-1" aria-hidden="true"></i>
                    新規登録
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
