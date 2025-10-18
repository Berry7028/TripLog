'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

import LogoutButton from './LogoutButton';
import { fetchAuthStatus } from '@/lib/client-api';

interface HeaderProps {
  currentUser?: {
    id: number;
    username: string;
  } | null;
}

const navItems = [
  { href: '/map', label: 'まっぷ' },
  { href: '/ranking', label: 'らんきんぐ' },
  { href: '/spots/add', label: 'とうこう' },
  { href: '/plan', label: 'ぷらん' },
];

export default function Header({ currentUser: initialUser }: HeaderProps) {
  const [currentUser, setCurrentUser] = useState(initialUser);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    if (initialUser === undefined) {
      fetchAuthStatus()
        .then((auth) => {
          if (auth.is_authenticated && auth.user) {
            setCurrentUser({ id: auth.user.id, username: auth.user.username });
          } else {
            setCurrentUser(null);
          }
        })
        .catch(() => {
          setCurrentUser(null);
        });
    }
  }, [initialUser]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      window.location.href = `/?search=${encodeURIComponent(searchQuery)}`;
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    window.location.href = '/';
  };

  return (
    <nav className="shadow-sm" style={{ backgroundColor: 'var(--brand-teal)' }}>
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-3">
          <Link href="/" className="text-xl font-bold text-white">
            <i className="fas fa-map-marked-alt me-2"></i>旅ログまっぷ
          </Link>

          <div className="hidden items-center gap-4 md:flex">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-white transition hover:text-gray-100"
              >
                {item.label}
              </Link>
            ))}
          </div>

          <form onSubmit={handleSearchSubmit} className="hidden md:flex items-center me-3">
            <div className="relative flex items-center">
              <input
                type="search"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="検索"
                className="rounded-pill border-0 px-4 py-1 pr-10 text-sm focus:outline-none"
                style={{ minWidth: '200px' }}
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute right-3 text-gray-500 hover:text-gray-700"
                >
                  ×
                </button>
              )}
            </div>
          </form>

          <div className="flex items-center gap-3">
            {currentUser ? (
              <>
                <Link
                  href="/my-spots"
                  className="flex items-center justify-center rounded-full text-white"
                  style={{
                    width: '34px',
                    height: '34px',
                    backgroundColor: 'rgba(255, 255, 255, 0.13)',
                  }}
                >
                  <i className="fas fa-user"></i>
                </Link>
                <Link href="/profile" className="text-white hover:text-gray-100 hidden md:inline">
                  {currentUser.username}
                </Link>
                <LogoutButton />
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-white hover:text-gray-100 flex items-center gap-1"
                >
                  <i className="fas fa-sign-in-alt"></i>
                  <span className="hidden md:inline">ログイン</span>
                </Link>
                <Link
                  href="/register"
                  className="text-white hover:text-gray-100 flex items-center gap-1"
                >
                  <i className="fas fa-user-plus"></i>
                  <span className="hidden md:inline">新規登録</span>
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
